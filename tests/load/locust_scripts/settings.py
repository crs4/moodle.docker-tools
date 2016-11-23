import os
import pprint
import subprocess
import socket
import logging

# MOODLE_URL = "http://" + socket.gethostname() + "/moodle"
# MOODLE_URL = "http://mep.crs4.it/moodle"
# MOODLE_URL = "http://omero-test.crs4.it/moodle"

# Users
USERS_FILENAME = 'users.csv'  # default filename containing test users
USER_PREFIX = 'testuser'  # default user prefix
USER_COHORT = 'test_users'  # default user cohort

# Questions
QUESTION_FILENAME = "questions.csv"

HTTP_CODES = [200, 300, 301, 302, 303, 304, 400, 401, 403, 404, 405, 406, 408, 500]

# TIMER_TYPE = "analytic"
# TIMER_TYPE = "average"

# StatsD server settings
STATSD_SERVER_ADDRESS = 'localhost'
STATSD_SERVER_PORT = 8125

# set the debug level
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)


# loads the configuration and update the environment
def read_config(config_filename):
    logging.debug("Reading config from: %s", config_filename)
    if not os.path.isfile(config_filename):
        logging.warn("Config %s filename not found!!!", config_filename)
    else:
        command = ['bash', '-c', 'source ' + config_filename + ' && env']
        proc = subprocess.Popen(command, stdout=subprocess.PIPE)
        for line in proc.stdout:
            (key, _, value) = line.partition("=")
            os.environ[key] = value.rstrip('\n')
        proc.communicate()
        pprint.pprint(dict(os.environ))


if not os.environ.has_key('SHARED_MOODLE_WWW_ROOT'):
    path = '../../../'
    config_filename = path + "config.sh"
    read_config(config_filename)
