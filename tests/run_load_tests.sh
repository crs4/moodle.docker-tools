#!/bin/sh

# the current path
CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# read general configuration
source ${CURRENT_DIR}/../config.sh

# server URL
SERVER_NAME=$1
shift

# configure dataset
DATASET=$1
DATASET_FOLDER="${CURRENT_DIR}/datasets/${DATASET}"
echo "DataSet folder: $DATASET_FOLDER..."
if [ ! -d ${DATASET_FOLDER} ]; then
	echo "DataSet ${DATASET} not found: folder ${DATASET_FOLDER} doesn't exist !!!"
	exit -1
fi
shift

# remove old links
rm -r questions.csv users.csv
# create new links
ln -s ${DATASET_FOLDER}/questions.csv questions.csv
ln -s ${DATASET_FOLDER}/users.csv users.csv

MODE=""
MASTER_IP=$(getent hosts master | awk '{ print $1 }')
if [[ ${1} = "slave" ]]; then
    MODE="--slave --master-host=${MASTER_IP}"
    shift
elif [[ ${1} = "master" ]]; then
    MODE="--master"
    shift
fi

# run tests
locust -f load/locust_scripts/tests.py ${MODE} --host=http://${SERVER_NAME}/moodle "$@"
