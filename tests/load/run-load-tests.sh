#!/usr/bin/env bash

# current dir
CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# import stats_utils
source ../../images/locust/stats_utils.sh

# set script
DOCKER_SCRIPT=../../images/locust/start.sh
SETUP_SCRIPT="load-test-setup.sh"

# locust script settings
CONFIG_FILE="config.yml"

# web server
#WEB_SERVER="http://cytest.crs4.it/moodle"
#WEB_SERVER="http://mep.crs4.it/moodle"
WEB_SERVER="https://omero-test.crs4.it:4443/moodle"

# Question DATASET
DATASET="../../tests/datasets/dev"

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
    # start time
    start_time=$(date +'%Y-%m-%d@%H:%M:%S')

    echo -e "\nRunning with ${users} users..."
    ${DOCKER_SCRIPT} -s ${SETUP_SCRIPT} \
                     --dataset ${DATASET} \
                     --config ${CONFIG_FILE} \
                     -w ${WEB_SERVER} \
                     -o "${OUTPUT_FOLDER}/${users}" \
                     --stats-conf moodle-stats.conf \
                     --timeout ${EXECUTION_TIME} \
                     -c ${users} -r ${users} --no-web

    # end time
    end_time=$(date +'%Y-%m-%d@%H:%M:%S')

    echo "START time: ${start_time}"
    echo "  END time: ${end_time}"

    # moodle stats
    collect_stats "http://cytest.crs4.it:8086" ${OUTPUT_FOLDER}/${users}/moodle \
            ${start_time} ${end_time} host-stats.conf
    # omero stats
    collect_stats "http://ome-cytest.crs4.it:8086" ${OUTPUT_FOLDER}/${users}/omero \
            ${start_time} ${end_time} host-stats.conf

    # wait for next test
    if [[ ${users} != ${USERS[*]: -1} ]]; then
        echo -e "\nWaiting for test to start..."
        sleep ${SLEEP_TIME}
    fi
done