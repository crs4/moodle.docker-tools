#!/usr/bin/env bash

CURRENT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Base path for sharing between DOCKER Host and containers
export SHARED_HOST_FOLDER="${HOME}/Development/Projects/Cytest/MoodleDocker"

# Shared www and data paths
export SHARED_WWW="${SHARED_HOST_FOLDER}/www"
export SHARED_LOG="${SHARED_HOST_FOLDER}/log"
export SHARED_DATA="${SHARED_HOST_FOLDER}/data"

# MySQL Configurations
export MYSQL_ALLOW_EMPTY_PASSWORD="yes"
export MYSQL_ROOT_PASSWORD="moodle"
export MYSQL_DATABASE="moodle"
export MYSQL_USER="moodle"
export MYSQL_PASSWORD="moodle"
export MYSQL_DATADIR="/var/lib/mysql"
export SHARED_MYSQL_DATADIR="${SHARED_DATA}/mysql"

# Moodle Configuration
export APACHE_WWW_ROOT="/var/www/html"
export MOODLE_WWW_ROOT="${APACHE_WWW_ROOT}/moodle"
export MOODLE_DATA_DIR="/var/www/moodledata"
export MOODLE_LOG_DIR="/var/log/apache2"
export SHARED_MOODLE_WWW_ROOT="${SHARED_WWW}/moodle"
export SHARED_MOODLE_LOG_DIR="${SHARED_LOG}/moodle"
export SHARED_MOODLE_DATA_DIR="${SHARED_DATA}/moodle"

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

# BACKUP folder
export MYSQL_BACKUPS_DIR="${CURRENT_PATH}/Backups"
