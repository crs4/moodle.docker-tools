#!/usr/bin/env bash

# script dir
CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# target dir
TARGET_DIR=${2:-".."}

# read general configuration
#source ${CURRENT_DIR}/config.sh
export CYTEST_CONFIGURATION_FILE="config.yml"

# configure dataset
DATASET=${1:-"prod"}
DATASET_FOLDER="${CURRENT_DIR}/../datasets/${DATASET}"

#DATASET_FOLDER="${DATASET}"
echo "DataSet folder: $DATASET_FOLDER..."
if [ ! -d ${DATASET_FOLDER} ]; then
	echo "DataSet ${DATASET} not found: folder ${DATASET_FOLDER} doesn't exist !!!"
	exit -1
fi

# remove old links
rm -r ${TARGET_DIR}/questions.csv ${TARGET_DIR}/users.csv

# create new links
ln -s ${DATASET_FOLDER}/questions.csv ${TARGET_DIR}//questions.csv
ln -s ${DATASET_FOLDER}/users.csv ${TARGET_DIR}//users.csv
