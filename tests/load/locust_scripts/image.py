import os
import api
import time
import copy
import threading
import logging
import math
import xml.etree.ElementTree as ET
from statsd import StatsClient
from settings import configuration


class Image():
    MIN_ZOOM_LEVEL = 8
    IMAGE_LOADER_POOL_SIZE = 6

    def __init__(self, browser, image_server, image_id, timer_registry=None, timer_name="load_DZI"):
        self._browser = browser
        self._image_id = image_id
        self._timer_registry = timer_registry
        self._timer_name = timer_name
        self._image_server_url = image_server
        self._logger = logging.getLogger("Image-" + image_id)
        self._stats = StatsClient(configuration["statsd"]["server_host"], configuration["statsd"]["server_port"])
        self._image_server = api.ImageServerAPI.new_instance(image_server, browser)
        # init image info
        self._info = Image.get_dzi_image_info(self._image_server, self._image_id, self._stats, timer_registry,
                                              timer_name)
        self._info["max_zoom_level"] = self.get_max_zoom_level(self._info)
        self._tile_loaded = []

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
        return int(scaled_width / self._info["tilesize"])  # + 1

    def columns(self, zoom_level):
        scaled_height = self._info["height"] * self.scale_factor(zoom_level)
        return int(scaled_height / self._info["tilesize"])  # + 1

    def get_tiles_info_by_level(self, current_level, frame_width=600, frame_height=500, reduction_factor=1):
        if reduction_factor <= 0:
            raise ValueError("Reduction factor must be greater than 0")
        counter = 0
        tiles_info = []
        max_rows = ((frame_width / self._info["tilesize"] + 1) / reduction_factor)
        max_cols = ((frame_height / self._info["tilesize"] + 1) / reduction_factor)
        # max_tiles_level = max_rows * max_cols
        for row in range(0, min(max_rows, self.rows(current_level)) + 1):
            for col in range(0, min(max_cols, self.columns(current_level)) + 1):
                tiles_info.append((current_level, row, col))
                counter += 1
        return tiles_info

    def load_tiles(self, zoom_level, frame_width=600, frame_height=500,
                   deep_load=True, multithreading=False, thread_pool_size=IMAGE_LOADER_POOL_SIZE,
                   force_reload=False, timer_name="Load Level Tiles"):
        tiles_info = []
        current_level = zoom_level
        while current_level >= 8 and current_level < self.max_zoom_level:
            level_distance = zoom_level - current_level
            reduction_factor = level_distance * 2 if level_distance > 0 else 1
            tiles_info.extend(self.get_tiles_info_by_level(current_level, frame_width, frame_height, reduction_factor))
            if deep_load:
                current_level -= 1
            else:
                break
        self._logger.debug("Tiles to LOAD %r", tiles_info)
        if multithreading:
            counter = 0
            image_loader_pool = [ImageTileLoaderThread(self, force_reload=force_reload)
                                 for i in range(0, thread_pool_size + 1)]
            for tile in tiles_info:
                thread_number = counter % len(image_loader_pool)
                image_loader_pool[thread_number].add_tile(tile)
                counter += 1
            start_time = time.time()
            for t in image_loader_pool:
                self._logger.debug("Tiles of thread %s: %r", t.getName(), t.tiles)
                t.start()
            for t in image_loader_pool:
                t.join()
        else:
            start_time = time.time()
            for tile_info in tiles_info:
                zoom_level, row, col = tile_info
                self._logger.debug("Loading tile %r", tile_info)
                self.load_tile(zoom_level, row, col, timer_name, force_reload=force_reload)
        latency = time.time() - start_time
        if self._timer_registry:
            self._timer_registry.add_timer(timer_name, start_time, latency)
        self._logger.debug("Latency for loading tiles @level" + str(zoom_level) + ": %s", latency)

    def load_tile(self, zoom_level, row, col, timer_name="LoadTile", force_reload=False):
        # check whether the tile has already been loaded
        tile_id = os.path.join(str(zoom_level), str(row), str(col))
        if tile_id not in self._tile_loaded or force_reload:

            #####
            # request_path = os.path.join(self._server, "ome_seadragon", "deepzoom", "get",
            #                             str(self._image_id) + "_files", str(zoom_level),
            #                             str(row) + "_" + str(col) + ".jpeg")

            # OmeroGateWay
            # request_path = os.path.join(self._image_server_url, "api", "deepzoom",
            #                             str(self._image_id) + "_files", str(zoom_level),
            #                             str(row) + "_" + str(col) + ".jpeg")
            #####

            start_time = time.time()
            with self._stats.timer("moodle.image.loadTile"):
                # resp = self._browser.get(request_path)
                resp = self._image_server.get_tile(self._image_id, zoom_level, row, col)
            latency = time.time() - start_time
            if self._timer_registry:
                # self._timer_registry.add_timer(timer_name, start_time, latency, request_path, resp.status_code)
                self._timer_registry.add_timer(timer_name, start_time, latency, resp.request.url, resp.status_code)
            assert (resp.status_code == 200), 'Bad HTTP Response: ' + str(resp.status_code)
            self._tile_loaded.append(tile_id)
        else:
            self._logger.debug("Tile %s already loaded", tile_id)

    def __str__(self):
        return "Image " + str(self._image_id)

    @staticmethod
    def get_dzi_image_info(image_server, image_id, stats, timer_registry, timer_name="DZI Retrieve"):
        info = {}
        # OmeSeadragon
        # request = os.path.join(server, "ome_seadragon", "deepzoom", "get", str(image_id) + ".dzi")
        # Omero Gateway
        # request = os.path.join(server, "api", "deepzoom", str(image_id))
        start_time = time.time()
        with stats.timer("moodle.image.loadDZI"):
            # response = browser.get(request, name="/get/dzi=[id]")
            response = image_server.get_dzi(image_id)
        latency = time.time() - start_time
        if timer_registry:
            timer_registry.add_timer(timer_name, start_time, latency, response.request.url, response.status_code)
        assert (response.status_code == 200), \
            'Bad HTTP Response: ' + str(response.status_code) + ", " + response.request.url
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


class ImageTileLoaderThread(threading.Thread):
    def __init__(self, image, timer_name="ImageTile", force_reload=False):
        threading.Thread.__init__(self)
        self._tiles = []
        self._image = image
        self._force_reload = force_reload
        self._timer_name = timer_name
        self._logger = logging.getLogger("TilesLoaderThread-" + self.getName())

    @property
    def tiles(self):
        return self._tiles

    def add_tile(self, tile_info):
        self._tiles.append(tile_info)

    def remove_tile(self, index):
        self._tiles.remove(index)

    def clear_tile_list(self):
        self._tiles[:] = []

    @property
    def tiles(self):
        return copy.deepcopy(self._tiles)

    @property
    def stopped(self):
        return self._stop.isSet()

    def stop(self):
        self._stop.set()

    def run(self):
        self._logger.debug("Thread %s start !!!", self.getName())
        for tile_info in self._tiles:
            zoom_level, row, col = tile_info
            self._logger.debug("Loading tile %r", tile_info)
            self._image.load_tile(zoom_level, row, col, self._timer_name, force_reload=self._force_reload)
        self._logger.debug("Thread %s end !!!", self.getName())
