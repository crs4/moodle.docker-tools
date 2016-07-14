import os
import time
import copy
import thread
import threading
import requests
import math
from timers import report_timers
import xml.etree.ElementTree as ET


class Image():
    def __init__(self, image_id, timer_registry=None, timer_name="DZI Retrieve"):
        self._image_id = image_id
        self._timer_registry = timer_registry
        self._timer_name = timer_name
        self._info = Image.get_dzi_image_info(self._image_id, timer_registry, timer_name)
        self._info["max_zoom_level"] = self.get_max_zoom_level(self._info)

    @property
    def image_info(self):
        return copy.deepcopy(self._info)

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
        return Image.get_scale_factor(level, self._info["max_zoom_level"])

    def rows(self, zoom_level):
        scaled_width = self._info["width"] * self.scale_factor(zoom_level)
        return int(scaled_width / self._info["tilesize"])

    def columns(self, zoom_level):
        scaled_height = self._info["height"] * self.scale_factor(zoom_level)
        return int(scaled_height / self._info["tilesize"])

    def __str__(self):
        return "Image " + str(self._image_id)

    @staticmethod
    def get_dzi_image_info(image_id, timer_registry=None, timer_name="DZI Retrieve"):
        info = {}
        start = time.time()
        response = requests.get("http://ome-cytest.crs4.it:8080/ome_seadragon/deepzoom/get/" + str(image_id) + ".dzi")
        latency = time.time() - start
        if timer_registry is not None:
            timer_registry[timer_name] = latency
            report_timers(timer_registry, timer_name, response, latency)
        # parse the response
        root = ET.fromstring(response.content)
        children = root.getchildren()
        if len(children) == 0:
            raise RuntimeError("Unable to find the 'SIZE' node")
        size_node = children[0]
        # set image info
        info["id"] = image_id
        info["format"] = root.get("Format")
        info["overlap"] = root.get("Overlap")
        info["tilesize"] = int(root.get("TileSize"))
        info["width"] = float(size_node.get("Width"))
        info["height"] = float(size_node.get("Height"))
        return info

    @staticmethod
    def get_max_zoom_level(img_info):
        x = float(img_info["width"])
        y = float(img_info["height"])
        return int(math.ceil(math.log(max(x, y), 2)))

    @staticmethod
    def get_scale_factor(level, max_level):
        if level > max_level:
            raise ValueError('Level %d is higher than max DZI level for the image' % level)
        return math.pow(0.5, max_level - level)


class ImageLoader(threading.Thread):
    def __init__(self, threadID, image, timer_registry=None, timer_name="Tile Retrieve"):
        threading.Thread.__init__(self)
        self._threadID = threadID
        self._image = image
        self._timer_registry = timer_registry
        self._timer_name = timer_name
        self._stop = threading.Event()
        self._server = os.environ["OMESEADRAGON_HOST"]

    @property
    def stopped(self):
        return self._stop.isSet()

    def stop(self):
        self._stop.set()

    def __str__(self):
        return "Thread " + self._threadID + " related to the " + str(self._image)

    def run(self):
        print "Starting " + self
        while not self._stop.isSet():
            start_time = time.time()
            resp = requests.get("http://ome-cytest.crs4.it:8080/ome_seadragon/deepzoom/get/7294_files/13/10_12.jpeg")
            latency = time.time() - start_time
            report_timers(self._timer_registry, self._timer_name, resp, latency)
        print "Exiting " + self
