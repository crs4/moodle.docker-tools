#!/usr/bin/env bash

# the path of this script
CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# load default settings
source ${CURRENT_DIR}/../../config.sh

# create and init DB for test results
mysql -h ${MYSQL_HOST} -u root -p${MYSQL_ROOT_PASSWORD} -e "create database ${LOAD_TEST_DB}";
mysql -h ${MYSQL_HOST} -u root -p${MYSQL_ROOT_PASSWORD} -e "GRANT ALL ON ${LOAD_TEST_DB}.* TO '${MYSQL_USER}'@'%';";
mysql -h ${MYSQL_HOST} -u root -p${MYSQL_ROOT_PASSWORD} ${LOAD_TEST_DB} < ./test-db.sql
