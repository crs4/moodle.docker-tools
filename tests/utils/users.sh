#!/usr/bin/env bash

# the path of this script
CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# set the filename
FILENAME="user.csv"
if [[ -n $1 ]]; then
    FILENAME=${1}
fi

# load default settings
source ${CURRENT_DIR}/../../config.sh

# dump the MySQL DB to the file ${FILENAME}
mysql -h ${MYSQL_HOST} -u ${MYSQL_USER} -p${MYSQL_PASSWORD}  \
      -e "SELECT username, password COLUMNS from mdl_user" ${MYSQL_DATABASE} > ${FILENAME}