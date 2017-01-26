import os
import csv
import time
import copy
import json
import logging
from image import Image
from urlparse import urlparse
from statsd import StatsClient
from bs4 import BeautifulSoup
from settings import configuration

# module logger
logger = logging.getLogger(__name__)

# preloaded list of questions
_QUESTION_LIST = None


class QUESTION_IMAGE_NAVIGATION_LOAD():
    LOW = 0
    MEDIUM = 1
    HIGH = 2

    @staticmethod
    def parse(load):
        value = load.upper()
        if value == "LOW":
            return QUESTION_IMAGE_NAVIGATION_LOAD.LOW
        elif value == "MEDIUM":
            return QUESTION_IMAGE_NAVIGATION_LOAD.MEDIUM
        elif value == "HIGH":
            return QUESTION_IMAGE_NAVIGATION_LOAD.HIGH
        raise ValueError("Unvalid value!!!")


def _get_server_url(browser, moodle_relative_path="moodle"):
    browser_url = urlparse(browser.host)
    moodle_url = browser_url.scheme + "://" + os.path.join(browser_url.hostname, "moodle")
    return (browser_url, moodle_url)


class Question():
    ZOOM_LEVEL_THINK_TIME = 3

    def __init__(self, id, name, type):
        self.id = id
        self.name = name
        self.type = type
        self._browser = None
        self._timer_registry = None
        self._timer_name = None
        self._server_info = None
        self._moodle_url = None
        self._info = None
        self._stats = StatsClient(configuration["statsd"]["server_host"], configuration["statsd"]["server_port"])
        self._logger = logging.getLogger("Question" + self.id)
        self._logger.setLevel(configuration["log"]["level"])

    @property
    def question_id(self):
        return self._question_id

    @property
    def info(self):
        return copy.deepcopy(self._info)

    @property
    def image(self):
        if not hasattr(self, "_image"):
            self._load_image()
        return self._image

    @property
    def zoom_level(self):
        zoom_level = self._info.get("image_properties").get("zoom_level") \
            if self._info.get("image_properties") else 0.0
        self._logger.debug("Current ZOOM level: %r", zoom_level)
        return zoom_level

    @property
    def width(self):
        return self._info["width"]

    @property
    def height(self):
        return self._info["height"]

    def __str__(self):
        return "Question { id: %s, name: %s, type: %s }" % (self.id, self.name, self.type)

    def __repr__(self):
        return self.__str__()

    def load(self, browser, host=None, timer_registry=None,
             timer_name="load_QuestionInfo", lazy_load_image=False):
        self._browser = browser
        self._timer_registry = timer_registry
        self._timer_name = timer_name
        self._server_info = host if host else _get_server_url(browser)
        self._moodle_url = self._server_info[1]
        self._info = load_question_info(browser, self._server_info, self.id, self._stats,
                                        timer_registry=timer_registry, timer_name=timer_name)
        self._logger.debug("Loaded question info: %r", self._info)
        if not lazy_load_image:
            self._load_image()

    def _load_image(self):
        self._image = Image(self._browser,
                            self._info["image_server"],
                            self._info.get("image_id"),
                            timer_registry=self._timer_registry)

    def scale_factor(self, level):
        return Question.get_scale_factor(level, self._info["max_zoom_level"])

    def rows(self, zoom_level):
        scaled_width = self._info["width"] * self.scale_factor(zoom_level)
        return int(scaled_width / self._info["tilesize"])

    def columns(self, zoom_level):
        scaled_height = self._info["height"] * self.scale_factor(zoom_level)
        return int(scaled_height / self._info["tilesize"])

    def navigate_image(self, load=QUESTION_IMAGE_NAVIGATION_LOAD.LOW, multithread=False,
                       frame_width=600, frame_height=500,
                       think_time_per_level=ZOOM_LEVEL_THINK_TIME, force_reload=False):
        zoom_levels = []
        image = self.image

        if isinstance(load, (str, unicode)):
            load = QUESTION_IMAGE_NAVIGATION_LOAD.parse(load)

        max_zoom_level = int(image.max_zoom_level) + 1
        current_zoom_level = int(round(self.zoom_level))
        if current_zoom_level < image.MIN_ZOOM_LEVEL:
            current_zoom_level = image.MIN_ZOOM_LEVEL
        self._logger.debug("CURRENT ZOOM LEVEL %s", self.zoom_level)
        self._logger.debug("MAX ZOOM LEVEL %s", image.max_zoom_level)
        if load == QUESTION_IMAGE_NAVIGATION_LOAD.LOW:
            zoom_levels.append(current_zoom_level)
        elif load == QUESTION_IMAGE_NAVIGATION_LOAD.MEDIUM:
            delta = int(current_zoom_level / 4)
            for level in range(current_zoom_level - delta, current_zoom_level + delta):
                if level < image.MIN_ZOOM_LEVEL:
                    continue
                if level >= max_zoom_level:
                    break
                zoom_levels.append(level)
        else:
            for level in range(image.MIN_ZOOM_LEVEL, int(image.max_zoom_level) + 1):
                zoom_levels.append(level)
                self._logger.debug("Level: %r", level)
        self._logger.debug("ZOOM LEVELs %r", zoom_levels)
        start_time = time.time()
        for level in zoom_levels:
            image.load_tiles(level, frame_width, frame_height, frame_height,
                             multithreading=multithread, force_reload=force_reload)
            time.sleep(think_time_per_level)
        latency = time.time() - start_time
        if self._timer_registry:
            self._timer_registry.add_timer("NavigationImage", start_time, latency)
        self._logger.debug("NavigationImage latency: %r", latency)
        self._logger.debug("ZOOM LEVELs: %r", zoom_levels)


def load_question_info(browser, host, question_id, stats,
                       moodle_relative_path="moodle",
                       timer_registry=None,
                       timer_name="Question info loading"):
    start_time = time.time()
    request_path = "/" + os.path.join("question", "preview.php?id=" + str(question_id))
    logging.debug("Loading question info @ %s", request_path)
    content = None
    with stats.timer("moodle.question.loadinfo"):
        response = browser.get(request_path, name="/question/preview.php?id=[qid]")
        stats.gauge('requests.total', 1, delta=True)
        if response is None or response.status_code != 200:
            stats.gauge("errors.{0}".format("question.preview"), 1, delta=True)
            stats.gauge("errors.total", 1, delta=True)
            raise RuntimeError("Error while loading question info")
        content = response.content
    latency = time.time() - start_time
    # register timers & counters
    if timer_registry:
        timer_registry.add_timer(timer_name, start_time, latency, request_path, response.code)
    # extract data
    viewer_config_el = None
    soup = BeautifulSoup(content, "html.parser")
    for i in soup.findAll("input"):
        if i.get("id") and "-config" in i.get("id"):
            viewer_config_el = i
            break
    if viewer_config_el is None:
        raise RuntimeError("Unable to find the viewer configuration")
    # parse and return the JSON data
    info = json.loads(viewer_config_el.get("value"))
    logging.debug("Loaded question INFO %r", info)
    return info


def get_questions(filename=configuration["questions"]["filename"],
                  delimiter=',', skip_header=True, as_dict=False,
                  force_reload=False):
    if not _QUESTION_LIST or force_reload:
        result = []
        if not os.path.isfile(filename):
            base_path = os.path.dirname(__file__)
            path = (base_path + "/../../") if base_path else '../../'
            filename = path + filename
            if not os.path.isfile(filename):
                raise Exception("Question list not found")
        with open(filename, 'rb') as csvfile:
            logger.info("Reading questions from file '%s'...", filename)
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            for question in reader:
                result.append(question) if as_dict \
                    else result.append(Question(question["id"], question["name"], question["type"]))
        return result
    return _QUESTION_LIST


# init question list
_QUESTION_LIST = get_questions()
