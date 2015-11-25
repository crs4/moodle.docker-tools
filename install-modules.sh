#!/bin/bash

CURRENT_DIR=$(pwd)
export MOODLE_PACKAGES_FOLDER=/opt/moodle-packages
export MOODLE_WWW=/var/www/html/moodle
BRANCH="master"

mkdir -p ${MOODLE_PACKAGES_FOLDER}

if [[ ! -d "${MOODLE_WWW}/repository/omero" ]]; then
	echo "Cloning the 'moodle.omero-repository' module"
	git clone https://github.com/kikkomep/moodle.omero-repository.git ${MOODLE_WWW}/repository/omero
	git fetch	
fi
echo "Updating the 'moodle.omero-repository' module ..."
cd ${MOODLE_WWW}/repository/omero
git checkout ${BRANCH}
git pull origin ${BRANCH}


if [[ ! -d "${MOODLE_WWW}/question/type/omeromultichoice" ]]; then
	echo "Cloning the 'moodle.omero-qtypes' module"
	git clone https://github.com/kikkomep/moodle.omero-qtypes.git ${MOODLE_WWW}/question/type/omeromultichoice
	git fetch	
fi
echo "Updating the 'moodle.omero-qtypes' module..."
cd ${MOODLE_WWW}/question/type/omeromultichoice
git checkout ${BRANCH}
git pull origin ${BRANCH}


if [[ ! -d "${MOODLE_WWW}/local/questionbanktagfilter" ]]; then
	echo "Cloning the 'moodle.qbank-tag-filter.git' module"
	git clone https://github.com/kikkomep/moodle.qbank-tag-filter.git ${MOODLE_WWW}/local/questionbanktagfilter
	git fetch	
fi
echo "Updating the 'moodle.qbank-tag-filter.git' module ..."
cd ${MOODLE_WWW}/local/questionbanktagfilter
git checkout ${BRANCH}
git pull origin develop


if [[ ! -d "${MOODLE_PACKAGES_FOLDER}/filepicker" ]]; then
	echo "Cloning the 'moodle.qbank-tag-filter.git' module"
	git clone https://github.com/kikkomep/moodle.omero-filepicker.git ${MOODLE_PACKAGES_FOLDER}/filepicker
	git fetch	
	cd ${MOODLE_PACKAGES_FOLDER}/filepicker
	git checkout ${BRANCH}
	git pull origin ${BRANCH}
	scripts/install	
else
	echo "Updating the 'moodle.qbank-tag-filter.git' module..."
	cd ${MOODLE_PACKAGES_FOLDER}/filepicker
	git checkout ${BRANCH}
	git pull origin ${BRANCH}
	scripts/deploy
fi
