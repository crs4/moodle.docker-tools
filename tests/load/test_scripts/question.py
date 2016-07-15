import os
import time
import copy
import json
from image import Image
from urlparse import urlparse
from bs4 import BeautifulSoup
from timers import report_timers


class Question():
    def __init__(self, browser, question_id, timer_registry=None, timer_name="load_QuestionInfo"):
        self._browser = browser
        self._question_id = question_id
        self._timer_registry = timer_registry
        self._timer_name = timer_name
        self._server_info = Question.get_server_url(browser)
        self._moodle_url = self._server_info[1]
        self._info = Question.load_question_info(browser, question_id,
                                                 timer_registry=timer_registry, timer_name=timer_name)

    @property
    def question_id(self):
        return self._question_id

    @property
    def info(self):
        return copy.deepcopy(self._info)

    @property
    def image(self):
        if not hasattr(self, "_image"):
            self._image = Image(self._browser,
                                self._info.get("image_id"),
                                self._info["image_server"],
                                timer_registry=self._timer_registry)
        return self._image

    @property
    def id(self):
        return self._info["id"]

    @property
    def max_zoom_level(self):
        return self._info["max_zoom_level"]

    @property
    def width(self):
        return self._info["width"]

    @property
    def height(self):
        return self._info["height"]

    def scale_factor(self, level):
        return Question.get_scale_factor(level, self._info["max_zoom_level"])

    def rows(self, zoom_level):
        scaled_width = self._info["width"] * self.scale_factor(zoom_level)
        return int(scaled_width / self._info["tilesize"])

    def columns(self, zoom_level):
        scaled_height = self._info["height"] * self.scale_factor(zoom_level)
        return int(scaled_height / self._info["tilesize"])

    def __str__(self):
        return "Question " + str(self._info["qname"])

    @staticmethod
    def get_server_url(browser, moodle_relative_path="moodle"):
        browser_url = urlparse(browser.geturl())
        moodle_url = browser_url.scheme + "://" + os.path.join(browser_url.hostname, "moodle")
        return (browser_url, moodle_url)

    @staticmethod
    def load_question_info(browser, question_id,
                           moodle_relative_path="moodle", timer_registry=None,
                           timer_name="Question info loading"):
        browser_info = Question.get_server_url(browser, moodle_relative_path=moodle_relative_path)
        start = time.time()
        response = browser.open(os.path.join(browser_info[1], "question", "preview.php?id=" + str(question_id)))
        latency = time.time() - start
        # register timers & counters
        if timer_registry is not None:
            timer_registry[timer_name] = latency
            report_timers(timer_registry, timer_name, start, latency, response)
        # extract data
        soup = BeautifulSoup(response.get_data(), "html.parser")
        for i in soup.findAll("input"):
            if i.get("id") and "-config" in i.get("id"):
                viewer_config_el = i
                break
        if viewer_config_el is None:
            raise RuntimeError("Unable to find the viewer configuration")
        # parse and return the JSON data
        info = json.loads(viewer_config_el.get("value"))
        return info
