#!/usr/bin/env bash

CURRENT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Load settings
source "${CURRENT_PATH}/settings.sh"

#############################################################################
# Paths on the SHARED_HOST_FOLDER
#############################################################################
export HOST_WWW_ROOT="${SHARED_HOST_FOLDER}/www"
export HOST_LOG_ROOT="${SHARED_HOST_FOLDER}/log"
export HOST_DATA_ROOT="${SHARED_HOST_FOLDER}/data"
## Moodle
export HOST_MOODLE_WWW_ROOT="${HOST_WWW_ROOT}/moodle"
export HOST_MOODLE_LOG_DIR="${HOST_LOG_ROOT}/moodle"
export HOST_MOODLE_DATA_DIR="${HOST_DATA_ROOT}/moodle"
## MySQL
export HOST_MYSQL_DATADIR="${HOST_DATA_ROOT}/mysql"


# MySQL Configurations
export MYSQL_HOST=$(hostname)
export MYSQL_ALLOW_EMPTY_PASSWORD="yes"
export MYSQL_ROOT_USER="root"
export MYSQL_ROOT_PASSWORD="moodle"
export MYSQL_DATABASE="moodle"
export MYSQL_USER="moodle"
export MYSQL_PASSWORD="moodle"
export MYSQL_DATADIR="/var/lib/mysql"
export LOAD_TEST_DB="load_tests"

# Moodle Configuration
export MOODLE_HOST=$(hostname)
export APACHE_WWW_ROOT="/var/www/html"
export MOODLE_WWW_ROOT="${APACHE_WWW_ROOT}/moodle"
export MOODLE_DATA_DIR="/var/www/moodledata"
export MOODLE_LOG_DIR="/var/log/apache2"

# certs Path
export CERTS_PATH=images/apache/certs

  #--> SSH KEY <--
SSH_KEY="${HOME}/.ssh/id_dsa.pub"
if [[ ! -f ${SSH_KEY} ]]; then
	SSH_KEY="${HOME}/.ssh/id_rsa.pub"
fi
export SSH_KEY_PATH=$SSH_KEY

# DOCKER IMAGE SETTINGS
export DOCKER_VOLUME_PREFIX="moodle-docker-"
export DOCKERHUB_REPOSITORY="crs4"
export DOCKERHUB_MYSQL_IMAGE="moodle-mysql"
export DOCKERHUB_APACHE_IMAGE="moodle-apache-php"
export DOCKERHUB_DROPBOX_IMAGE="moodle-dropbox"
export DOCKERHUB_LOCUST_IMAGE="locust"

# BACKUP folder
export MYSQL_BACKUPS_DIR="${CURRENT_PATH}/Backups"
