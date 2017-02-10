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

# servers
WEB_SERVER_HOSTNAME="omero-test.crs4.it"
IMAGE_SERVER_HOSTNAME="omero-test.crs4.it"

# web server
#WEB_SERVER="http://cytest.crs4.it/moodle"
#WEB_SERVER="http://mep.crs4.it/moodle"
MOODLE_URL="https://${WEB_SERVER_HOSTNAME}:4443/moodle"

# Question DATASET
DATASET="../../tests/datasets/dev"

# set execution time
EXECUTION_TIME=$((10 * 60))

# set list of number of users
USERS=($(seq 10 10 300))

# HATCH_RATE
HATCH_RATE=0.16666667

# output folder
OUTPUT_FOLDER="results/"$(date +'%Y%m%d%H%M%S')

# set sleep time
SLEEP_TIME=$((2 * 60))

# run and collect results
for users in "${USERS[@]}"
do
    # start time
    start_time=$(date)

    echo -e "\nRunning with ${users} users..."
    ${DOCKER_SCRIPT} -s ${SETUP_SCRIPT} \
                     --dataset ${DATASET} \
                     --config ${CONFIG_FILE} \
                     -w ${MOODLE_URL} \
                     -o "${OUTPUT_FOLDER}/${users}" \
                     --stats-conf moodle-stats.conf \
                     --timeout ${EXECUTION_TIME} \
                     -c ${users} -r ${HATCH_RATE} --no-web

    # end time
    end_time=$(date)

    echo "START time: ${start_time}"
    echo "  END time: ${end_time}"

    # moodle stats
    s_time=$(date -d "$start_time" '+%Y-%m-%d@%H:%M:%S')
    e_time=$(date -d "$end_time" '+%Y-%m-%d@%H:%M:%S')
    collect_stats "http://${WEB_SERVER_HOSTNAME}:8086" ${OUTPUT_FOLDER}/${users}/moodle \
            ${s_time} ${e_time} host-stats.conf

    # omero stats
#    s_time=$(date -d "$start_time -1 hours" '+%Y-%m-%d@%H:%M:%S')
#    e_time=$(date -d "$end_time -1 hours" '+%Y-%m-%d@%H:%M:%S')
#    collect_stats "http://${IMAGE_SERVER_HOSTNAME}:8086" ${OUTPUT_FOLDER}/${users}/omero \
#            ${s_time} ${e_time} host-stats.conf

    # wait for next test
    if [[ ${users} != ${USERS[*]: -1} ]]; then
        echo -e "\nWaiting for test to start..."
        sleep ${SLEEP_TIME}
    fi
done
