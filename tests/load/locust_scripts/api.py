import logging
import requests
from os import path
from json import loads
from settings import configuration
from abc import ABCMeta, abstractmethod


class ImageServerAPI:
    __metaclass__ = ABCMeta

    def __init__(self, image_server_url, http_client=None):
        self._oauth_enabled = False
        self._client_id = None
        self._client_secret = None
        self._image_server_url = image_server_url
        self._current_token = None
        self._http_client = http_client
        if http_client is None:
            self._http_client = requests
        self._logger = logging.getLogger(self.__class__.__name__)

    @property
    def image_server_url(self):
        return self._image_server_url

    def enable_oauth(self, enabled):
        self._oauth_enabled = enabled

    def is_oauth_enabled(self):
        return self._oauth_enabled

    def set_oauth_credentials(self, client_id, client_secret):
        self._client_id = client_id
        self._client_secret = client_secret

    def get_oauth_token(self):
        if not self._oauth_enabled:
            raise RuntimeError("OAuth not enabled")

        if not self._client_id or not self._client_secret:
            raise RuntimeError("Client ID and/or secret are not defined!!!")

        if self._current_token is None:
            token_endpoint = path.join(self._image_server_url, "oauth2", "token") + "/"
            response = self._http_client.post(token_endpoint,
                                              data={"client_id": self._client_id,
                                                    "client_secret": self._client_secret,
                                                    "grant_type": "client_credentials"
                                                    }
                                              )
            if response.status_code != 200:
                raise RuntimeError("Error during OAuth authorization")
            self._current_token = loads(response.content)
        return self._current_token

    def request(self, url, method="get", params={}, headers={}, name=None):
        if self.is_oauth_enabled():
            token = self.get_oauth_token()
            headers["Authorization"] = "Bearer " + token["access_token"]
            headers["Authorization"] = "Bearer " + token["access_token"]
        # FIXME: only get is supported
        self._logger.debug("Request path: %s", url)
        return self._http_client.get(url, headers=headers, params=params, name=name)

    @abstractmethod
    def get_dzi(self, image_id):
        pass

    @abstractmethod
    def get_tile(self, image_id, zoom_level, row, col):
        pass

    @staticmethod
    def new_instance(image_server_url, http_client=None):
        instance = configuration["image_server"]["api"](image_server_url, http_client)
        if configuration["oauth"]["enabled"]:
            instance.enable_oauth(True)
            instance.set_oauth_credentials(configuration["oauth"]["client_id"],
                                           configuration["oauth"]["client_secret"])
        return instance


class OmeSeadragon(ImageServerAPI):
    def get_dzi(self, image_id):
        url = path.join(self.image_server_url, "ome_seadragon", "deepzoom", "get", str(image_id) + ".dzi")
        print url
        return self.request(url, name="/get/dzi=[id]")

    def get_tile(self, image_id, zoom_level, row, col):
        url = path.join(self._image_server_url, "ome_seadragon", "deepzoom", "get",
                        str(image_id) + "_files", str(zoom_level),
                        str(row) + "_" + str(col) + ".jpeg")
        print url
        return self.request(url, name="/get/tile?id=[id]")


class OmeSeadragonGateway(ImageServerAPI):
    def get_dzi(self, image_id):
        url = path.join(self._image_server_url, "api", "deepzoom", str(image_id) + ".dzi") + "/"
        print url
        return self.request(url, name="/get/dzi=[id]")

    def get_tile(self, image_id, zoom_level, row, col):
        url = path.join(self._image_server_url, "api", "deepzoom",
                        str(self._image_id) + "_files", str(zoom_level),
                        str(row) + "_" + str(col) + ".jpeg")
        print url
        return self.request(url, name="/get/tile?id=[id]")
