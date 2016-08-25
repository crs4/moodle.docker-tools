import os
import time
import copy
import json
import csv
import settings
from image import Image
from urlparse import urlparse
from bs4 import BeautifulSoup


class QUESTION_IMAGE_NAVIGATION_LOAD():
    LOW = 0
    MEDIUM = 1
    HIGH = 2


def _get_server_url(browser, moodle_relative_path="moodle"):
    browser_url = urlparse(browser.geturl())
    moodle_url = browser_url.scheme + "://" + os.path.join(browser_url.hostname, "moodle")
    return (browser_url, moodle_url)


class Question():
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
        return self._info.get("image_properties").get("zoom_level")

    @property
    def width(self):
        return self._info["width"]

    @property
    def height(self):
        return self._info["height"]

    def __str__(self):
        return "id: %s, name: %s, type: %s" % (self.id, self.name, self.type)

    def load(self, browser, timer_registry=None,
             timer_name="load_QuestionInfo", lazy_load_image=False):
        self._browser = browser
        self._timer_registry = timer_registry
        self._timer_name = timer_name
        self._server_info = _get_server_url(browser)
        self._moodle_url = self._server_info[1]
        self._info = load_question_info(browser, self.id,
                                        timer_registry=timer_registry, timer_name=timer_name)
        if not lazy_load_image:
            self._load_image()

    def _load_image(self):
        self._image = Image(self._browser,
                            self._info.get("image_id"),
                            self._info["image_server"],
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
                       frame_width=600, frame_height=500, think_time_per_level=3):
        zoom_levels = []
        image = self.image
        current_zoom_level = int(round(self.zoom_level))
        print "CURRENT ZOOM LEVEL %s" % self.zoom_level
        print "MAX ZOOM LEVEL %s" % image.max_zoom_level
        if load == QUESTION_IMAGE_NAVIGATION_LOAD.LOW:
            zoom_levels.append(current_zoom_level)
        elif load == QUESTION_IMAGE_NAVIGATION_LOAD.MEDIUM:
            delta = int(current_zoom_level / 4)
            for level in range(current_zoom_level - delta, current_zoom_level + delta):
                zoom_levels.append(level)
                print level
        else:
            for level in range(8, int(image.max_zoom_level) + 1):
                zoom_levels.append(level)
                print level
        for level in zoom_levels:
            image.load_tiles(level, frame_width, frame_height, frame_height, multithreading=multithread)
            time.sleep(think_time_per_level)
        print "ZOOM LEVELs:", zoom_levels


def load_question_info(browser, question_id,
                       moodle_relative_path="moodle", timer_registry=None,
                       timer_name="Question info loading"):
    browser_info = _get_server_url(browser, moodle_relative_path=moodle_relative_path)
    start_time = time.time()
    response = browser.open(os.path.join(browser_info[1], "question", "preview.php?id=" + str(question_id)))
    latency = time.time() - start_time
    # register timers & counters
    timer_registry.add_timer(timer_name, start_time, latency, response.code)
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


def get_questions(filename=settings.QUESTION_FILENAME, delimiter=',', skip_header=True, as_dict=False):
    result = []
    filename = settings.QUESTION_FILENAME
    if not os.path.isfile(filename):
        base_path = os.path.dirname(__file__)
        path = (base_path + "/../../") if base_path else '../../'
        filename = path + filename
        if not os.path.isfile(filename):
            raise Exception("Question list not found")
        with open(filename, 'rb') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=delimiter)
            for question in reader:
                result.append(question) if as_dict \
                    else result.append(Question(question["id"], question["name"], question["type"]))
    return result
