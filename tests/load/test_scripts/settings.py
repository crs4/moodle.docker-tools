import os
import pprint
import subprocess
import socket
import logging

# MOODLE_URL = "http://" + socket.gethostname() + "/moodle"
MOODLE_URL = "http://mep.crs4.it/moodle"
# MOODLE_URL = "http://omero-test.crs4.it/moodle"


# Users
USERS_FILENAME = 'users.csv'  # default filename containing test users
USER_PREFIX = 'testuser'  # default user prefix
USER_COHORT = 'test_users'  # default user cohort

# Questions
QUESTION_FILENAME = "questions.csv"

HTTP_CODES = [200, 300, 301, 302, 303, 304, 400, 401, 403, 404, 405, 406, 408, 500]

# TIMER_TYPE = "analytic"
TIMER_TYPE = "average"

# set the debug level
logging.basicConfig(level=logging.DEBUG)

# loads the configuration and update the environment
if not os.environ.has_key('SHARED_MOODLE_WWW_ROOT'):
    path = '../../../'
    config_filename = path + "config.sh"
    print config_filename
    if not os.path.isfile(config_filename):
        raise Exception("Config filename not found")

    command = ['bash', '-c', 'source ' + config_filename + ' && env']

    proc = subprocess.Popen(command, stdout=subprocess.PIPE)

    for line in proc.stdout:
        (key, _, value) = line.partition("=")
        os.environ[key] = value

    proc.communicate()

    pprint.pprint(dict(os.environ))
