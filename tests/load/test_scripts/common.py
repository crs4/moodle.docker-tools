import os
import abc
import time
import mechanize
from os import path
from bs4 import BeautifulSoup
from urlparse import urlparse
from settings import MOODLE_URL
from timers import TimerRegistry


def get_server_url(browser, moodle_relative_path="moodle"):
    browser_url = urlparse(browser.geturl())
    moodle_url = browser_url.scheme + "://" + os.path.join(browser_url.hostname, "moodle")
    # return (browser_url, moodle_url)
    return moodle_url


class BaseTransaction(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.custom_timers = {}

    @abc.abstractmethod
    def transaction_name(self):
        pass

    @abc.abstractmethod
    def transaction_flow(self):
        pass

    def _make_browser(self):
        browser = mechanize.Browser()
        browser.set_handle_robots(False)
        self._browser = browser
        return browser

    def _get_form(self, browser, form_id, disable_read_only=True, select_form=True):
        count = 0
        for f in browser.forms():
            if f.attrs.has_key("id") and f.attrs["id"] == form_id:
                if disable_read_only:
                    f.set_all_readonly(False)
                if select_form:
                    browser.select_form(nr=count)
                return f
            count += 1
        return None

    def _build_path(self, relative_url, base_path=MOODLE_URL, params={}):
        p = base_path + "/" + relative_url
        return p

    def load_current_page_resources(self, browser, timer_registry=None):
        if not browser or not browser.response:
            return
        resp = browser.response()
        if not resp:
            return
        data = resp.get_data()
        if not data:
            return
        page = BeautifulSoup(data, "html.parser")
        for script in page.findAll("script"):
            if script.get("src"):
                print "loading %s" % script.get("src")
                start_time = time.time()
                browser.open_novisit(script.get("src"))
                latency = time.time() - start_time
                if timer_registry:
                    timer_registry.add_timer("LoadingScript", start_time, latency)
                    print timer_registry._raw_timers

    def run(self):
        print "Custom timer before", self.custom_timers
        start_time = time.time()
        transaction_flow_id = "Transaction-" + self.transaction_name()
        timer_registry = TimerRegistry(self)
        self.transaction_flow(timer_registry)
        latency = time.time() - start_time
        timer_registry.add_timer("Transaction-" + self.transaction_name(), start_time, latency)
        timer_registry.write_timers_to_db()
        print "Ending: %s" % str(transaction_flow_id)
        print "Custom timer after", self.custom_timers

    @staticmethod
    def go_to_page(timer_registry, browser, relative_path, base_path=MOODLE_URL, params=None, timer_name=None,
                   sleep_time=0):
        start_time = time.time()
        print "PATH: %s" % path.join(base_path, relative_path)
        resp = browser.open(path.join(base_path, relative_path))
        latency = time.time() - start_time
        timer_registry.add_timer(timer_name, start_time, latency, resp.code)
        assert (resp.code == 200), 'Bad HTTP Response: ' + str(resp.code)
        return resp
