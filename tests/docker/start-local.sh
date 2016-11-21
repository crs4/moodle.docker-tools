#!/usr/bin/env bash

IMAGE_NAME="crs4/locust"
WEB_APP_ADDRESS="http://omero-test.crs4.it/moodle"
LOCUST_SCRIPT="/home/tester/docker-tools/tests/load/locust_scripts/tests.py"
INIT_SCRIPT="/scripts/init.sh"

DATASET_FOLDER="$(pwd)/../datasets"
INIT_SCRIPT_FOLDER="$(pwd)/../docker"

docker run -it --rm \
    -v ${DATASET_FOLDER}:"/datasets" \
    -v ${INIT_SCRIPT_FOLDER}:"/scripts" \
    -p "18086:8086"  \
    -p "18083:8083"  \
    -p "18088:8088"  \
    -p "18089:8089"  \
    -p "18090:10000" \
    ${IMAGE_NAME} \
    start.sh local ${WEB_APP_ADDRESS} ${LOCUST_SCRIPT} ${INIT_SCRIPT}
