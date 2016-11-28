#!/usr/bin/env bash

# clone the repository
GIT_TARGET=/home/tester/docker-tools
git clone https://github.com/kikkomep/moodle.docker-tools.git ${GIT_TARGET}
cd ${GIT_TARGET}
git checkout load-tests
cd tests
pip install -r requirements.txt
ln -s /datasets datasets

# script dir
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# the current path
CURRENT_DIR="${GIT_TARGET}"

# read general configuration
source ${CURRENT_DIR}/config.sh

# configure dataset
DATASET=$1
#DATASET_FOLDER="${CURRENT_DIR}/tests/datasets/${DATASET}"
DATASET_FOLDER="${DATASET}"
echo "DataSet folder: $DATASET_FOLDER..."
if [ ! -d ${DATASET_FOLDER} ]; then
	echo "DataSet ${DATASET} not found: folder ${DATASET_FOLDER} doesn't exist !!!"
	exit -1
fi

# remove old links
rm -r questions.csv users.csv

# create new links
ln -s ${DATASET_FOLDER}/questions.csv questions.csv
ln -s ${DATASET_FOLDER}/users.csv users.csv