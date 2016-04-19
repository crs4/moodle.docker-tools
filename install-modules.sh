#!/bin/bash

# paths
CURRENT_DIR=$(pwd)
MOODLE_PACKAGES_FOLDER=/tmp/moodle-packages # temp folder where Moodle packages are downloaded
export MOODLE_WWW=$(source config.sh && echo ${SHARED_MOODLE_WWW_ROOT};)

# github settings
GITHUB_USER="kikkomep"
BRANCH="develop"
USE_SSH=true
PRESERVE_HISTORY=true

# build github prefix & suffix
GITHUB_REPOSITORY_SUFFIX=".git"
GITHUB_REPOSITORY_PREFIX="https://github.com/${GITHUB_USER}/moodle."
if [[ ${USE_SSH} = true ]]; then
	GITHUB_REPOSITORY_PREFIX="git@github.com:${GITHUB_USER}/moodle."
fi

# create the temp folder for downloading packages
mkdir -p ${MOODLE_PACKAGES_FOLDER}

# list of required modules
MODULES=("omero-repository" "omero-filepicker" "omero-qtypes" "qbank-tag-filter")

# module targets (relative to MOODLE_WWW)
TARGETS=("repository/omero" "lib/form/omerofilepicker" "question/type" "local/questionbanktagfilter")

# install or update MODULES
for i in $(seq 0 1 $((${#MODULES[@]}-1)))
do
	MODULE=${MODULES[${i}]}
	TARGET=${TARGETS[${i}]}
	GITHUB_REPOSITORY=${GITHUB_REPOSITORY_PREFIX}${MODULE}${GITHUB_REPOSITORY_SUFFIX}
	MODULE_TEMP_FOLDER=${MOODLE_PACKAGES_FOLDER}/${MODULE}
	MODULE_TARGET_FOLDER=${MOODLE_WWW}/${TARGET}
	if [[ ! -d "${MODULE_TEMP_FOLDER}" ]]; then
		echo "Cloning the 'moodle.${MODULE}' module"
		git clone ${GITHUB_REPOSITORY} ${MODULE_TEMP_FOLDER}
		git fetch
	fi
	echo "Updating the 'moodle.${MODULE}' module ..."
	cd ${MODULE_TEMP_FOLDER}
	git checkout ${BRANCH}
	git pull origin ${BRANCH}
	rsync -avt ${MODULE_TEMP_FOLDER}/ ${MODULE_TARGET_FOLDER}
	if [[ ${PRESERVE_HISTORY} = false ]]; then
		rm -Rf ${MODULE_TARGET_FOLDER}/.git
	fi
	if [[ -f ${MODULE_TARGET_FOLDER}/register.sh ]]; then
		${MODULE_TARGET_FOLDER}/register.sh
	fi
done
