import os
import yaml
import pprint
import logging
import subprocess

ENV_VAR_CONFIG_FILE = "CYTEST_CONFIGURATION_FILE"

# default configuration
DEFAULT_CONFIG = {
    "dataset": {
        "folder": "../../"
    },
    "users": {
        "filename": "users.csv",
        "prefix": "testuser",
        "cohort": "test_users"
    },
    "questions": {
        "filename": "questions.csv"
    },
    "http": {
        "codes": [200, 300, 301, 302, 303, 304, 400, 401, 403, 404, 405, 406, 408, 500]
    },
    "statsd": {
        "server_host": "localhost",
        "server_port": "8125"
    },
    "oauth": {
        "enabled": "False",
        "client_id": "",
        "client_secret": ""
    },
    "image_server": {
        "api": "OmeSeadragon"
    }
}

# set the debug level
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)


# read configuration
def get_configuration(filename=None):
    config = DEFAULT_CONFIG.copy()
    if filename is None and os.environ.has_key(ENV_VAR_CONFIG_FILE):
        filename = os.environ[ENV_VAR_CONFIG_FILE]
        with open(filename) as fp:
            config.update(yaml.load(fp))
    return config


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


# update environment
if not os.environ.has_key('SHARED_MOODLE_WWW_ROOT'):
    path = '../../../'
    config_filename = path + "config.sh"
    read_config(config_filename)

# read configuration
configuration = get_configuration()
