import socket
import logging

#MOODLE_URL = "http://" + socket.gethostname() + "/moodle"
MOODLE_URL = "http://mep.crs4.it/moodle"

HTTP_CODES = [200, 300, 301, 302, 303, 304, 400, 401, 403, 404, 405, 406, 408, 500]

#TIMER_TYPE = "analytic"
TIMER_TYPE = "average"


logging.basicConfig(level=logging.DEBUG)