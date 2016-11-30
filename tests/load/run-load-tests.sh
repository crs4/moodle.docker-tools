#!/usr/bin/env bash

# import stats_utils
source ../../images/locust/stats_utils.sh

# set script
DOCKER_SCRIPT=../../images/locust/start.sh
SETUP_SCRIPT="load-test-setup.sh"

# web server
WEB_SERVER="http://cytest.crs4.it/moodle"

# Question DATASET
DATASET="../../tests/datasets/prod"

# set execution time
EXECUTION_TIME=$((10 * 60))

# set list of number of users
USERS=($(seq 10 10 300))

# output folder
OUTPUT_FOLDER="results"

# set sleep time
SLEEP_TIME=$((2 * 60))

# run and collect results
for users in "${USERS[@]}"
do
    echo -e "\nRunning with ${users} users..."
    ${DOCKER_SCRIPT} -s ${SETUP_SCRIPT} \
                     -w ${WEB_SERVER} \
                     --dataset ${DATASET} \
                     -o "${OUTPUT_FOLDER}/${users}" \
                     --timeout ${EXECUTION_TIME} \
                     -c ${users} -r ${users} --no-web
    # wait for next test
    if [[ ${users} != ${USERS[*]: -1} ]]; then
        echo -e "\nWaiting for test to start..."
        sleep ${SLEEP_TIME}
    fi
done