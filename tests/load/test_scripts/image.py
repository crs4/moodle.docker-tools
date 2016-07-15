import os
import time
import copy
import threading
import requests
import math
import xml.etree.ElementTree as ET
from timers import report_timers


class Image():
    def __init__(self, browser, image_id, image_server, timer_registry=None, timer_name="load_DZI"):
        self._browser = browser
        self._image_id = image_id
        self._timer_registry = timer_registry
        self._timer_name = timer_name
        self._server = image_server
        self._info = Image.get_dzi_image_info(self._image_id, timer_registry, timer_name)
        self._info["max_zoom_level"] = self.get_max_zoom_level(self._info)

    @property
    def info(self):
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
        return int(scaled_width / self._info["tilesize"]) + 1

    def columns(self, zoom_level):
        scaled_height = self._info["height"] * self.scale_factor(zoom_level)
        return int(scaled_height / self._info["tilesize"]) + 1

    def load_tiles(self, zoom_level, frame_width=600, frame_height=500,
                   deep_load=True, multithreading=False, timer_name="LoadTiles"):
        threads = []
        counters = {}
        current_level = zoom_level
        while current_level >= 8:
            if multithreading:
                t = ImageLoader(self.__str__() + "@" + str(current_level), self,
                                current_level, frame_width, frame_height, timer_name="Tile Retrieve")
                threads.append(t)
                t.start()
            else:
                counter = 0
                level_distance = zoom_level - current_level
                reduction_factor = level_distance * 2 if level_distance > 0 else 1
                max_rows = ((frame_width / self._info["tilesize"] + 1) / reduction_factor)
                max_cols = ((frame_height / self._info["tilesize"] + 1) / reduction_factor)
                # max_tiles_level = max_rows * max_cols
                start_time = time.time()
                for row in range(0, min(max_rows, self.rows(current_level)) + 1):
                    for col in range(0, min(max_cols, self.columns(current_level)) + 1):
                        self.load_tile(current_level, row, col)
                        counter += 1
                latency = time.time() - start_time
                report_timers(self._timer_registry, timer_name, start_time, latency)
                counters[current_level] = counter

            if deep_load:
                current_level -= 1
            else:
                break
        if multithreading:
            for t in threads:
                t.join()
        print counters

    def load_tile(self, zoom_level, row, col, timer_name="LoadTile"):
        start_time = time.time()
        request_path = os.path.join(self._server, "ome_seadragon", "deepzoom", "get",
                                    str(self._image_id) + "_files", str(zoom_level),
                                    str(row) + "_" + str(col) + ".jpeg")
        print "Request path: %s" % request_path
        resp = requests.get(request_path)
        latency = time.time() - start_time
        report_timers(self._timer_registry, timer_name, start_time, latency, resp)

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
            report_timers(timer_registry, timer_name, start, latency, response)
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
    def __init__(self, threadID, image,
                 zoom_level, frame_width=600, frame_height=500,
                 timer_name="Tile Retrieve"):
        threading.Thread.__init__(self)
        self._threadID = threadID
        self._image = image
        self._zoom_level = zoom_level
        self._frame_width = frame_width
        self._frame_height = frame_height
        self._timer_name = timer_name
        self._stop = threading.Event()

    @property
    def stopped(self):
        return self._stop.isSet()

    def stop(self):
        self._stop.set()

    def __str__(self):
        return "Thread " + self._threadID + " related to the " + str(self._image)

    def run(self):
        print "Starting " + str(self)
        self._image.load_tiles(self._zoom_level, self._frame_width, self._frame_height, False, False)
        print "Exiting " + str(self)
