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
EXECUTION_TIME=$((20))

# set list of number of users
#USERS=($(seq 10 10 300))
USERS=($(seq 1 10 1))

# output folder
OUTPUT_FOLDER="results"

# run and collect results
for users in "${USERS[@]}"
do
    echo "Running with $users..."
    ${DOCKER_SCRIPT} -s ${SETUP_SCRIPT} \
                     -w ${WEB_SERVER} \
                     --dataset ${DATASET} \
                     -o "${OUTPUT_FOLDER}/${users}" \
                     --timeout ${EXECUTION_TIME} \
                     -c ${users} -r ${users} --no-web
done