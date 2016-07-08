import abc
import time
import socket
import mechanize
from os import path

BASE_URL = "http://" + socket.gethostname() + "/moodle"

HTTP_CODES = [200, 300, 301, 302, 303, 304, 400, 401, 403, 404, 405, 406, 408, 500]


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

    def _add_time(self, timer_name, timer_value):
        self.custom_timers[timer_name] = timer_value

    def _make_browser(self):
        browser = mechanize.Browser()
        browser.set_handle_robots(False)
        self._browser = browser
        return browser

    def _get_form(self, browser, form_id, disable_read_only=True, select_form=True):
        count = 0
        for f in browser.forms():
            if f.attrs["id"] == form_id:
                if disable_read_only:
                    f.set_all_readonly(False)
                if select_form:
                    browser.select_form(nr=count)
                return f
            count += 1
        return None

    def _build_path(self, relative_url, params={}):
        p = BASE_URL + "/" + relative_url
        return p

    def _go_to_page(self, browser, relative_path, base_path=BASE_URL, params=None, timer_name=None, sleep_time=0):

        start_time = time.time()

        resp = browser.open(path.join(base_path, relative_path))
        latency = time.time() - start_time

        if timer_name:
            self.custom_timers[timer_name] = latency

        if resp.code in HTTP_CODES:
            self.custom_timers["CODE_" + str(resp.code)] = 1
            for code in HTTP_CODES:
                if code != resp.code:
                    self.custom_timers["CODE_" + str(code)] = 0

        assert (resp.code == 200), 'Bad HTTP Response: ' + str(resp.code)

        return resp

    def run(self):
        start_time = time.time()
        self.transaction_flow()
        end_time = time.time() - start_time
        self._add_time(self.transaction_name(), end_time)
