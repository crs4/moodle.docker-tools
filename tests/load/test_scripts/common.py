import os
import abc
import time
import mechanize
from os import path
from urlparse import urlparse
from settings import MOODLE_URL


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

    def _go_to_page(self, browser, relative_path, base_path=MOODLE_URL, params=None, timer_name=None, sleep_time=0):
        start_time = time.time()
        print "PATH: %s" % path.join(base_path, relative_path)
        resp = browser.open(path.join(base_path, relative_path))
        latency = time.time() - start_time
        report_timers(self.custom_timers, timer_name, start_time, latency, resp)
        assert (resp.code == 200), 'Bad HTTP Response: ' + str(resp.code)
        return resp

    def run(self):
        start_time = time.time()
        self.transaction_flow()
        end_time = time.time() - start_time
        self._add_time(self.transaction_name(), end_time)
