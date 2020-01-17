#!/bin/bash

DATASET=${1:-"dev"}

# set MOODLE URL
MOODLE_URL="https://omero-test.crs4.it:4443/moodle"

# load configuration
source load-test-setup-local.sh ${DATASET}

# launch tests
locust -f locust_scripts/tests.py --host=${MOODLE_URL}
