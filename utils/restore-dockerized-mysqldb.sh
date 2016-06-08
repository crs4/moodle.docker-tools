#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# load configuration
source ${DIR}/../config.sh

# read the DUMP filename
MYSQL_DUMP=$1
if [[ ! -f ${MYSQL_DUMP} ]]; then
  echo "${MYSQL_DUMP} doesn't exist!!!";
  exit -1;
fi
# normalization of DUMP filename
MYSQL_DUMP=$(realpath ${MYSQL_DUMP})

# create the 'configured' script
envsubst '$MYSQL_DATABASE:$MYSQL_ROOT_PASSWORD:$MYSQL_USER:$MYSQL_PASSWORD' \
          < $(pwd)/utils/restore-mysqldb.sh \
          > $(pwd)/utils/restore-mysqldb-configured.sh

# copy utility files
docker run -it --rm \
           -v $(pwd)/utils/restore-mysqldb-configured.sh:/utils/restore-mysqldb.sh \
           -v  ${MYSQL_DUMP}:/mysql-dump.sql \
           -v moodle-docker-mysql-data:/mysql-data \
           ubuntu bash -c "mkdir -p /mysql-data/tmp && cp /utils/restore-mysqldb.sh /mysql-data/tmp/ && cp /mysql-dump.sql /mysql-data/tmp/"

# perform the DB update
docker exec -it dockertools_mysql_1 bash -c \
       "/var/lib/mysql/tmp/restore-mysqldb.sh /var/lib/mysql/tmp/mysql-dump.sql"

# cleaning
docker run -it --rm \
           -v moodle-docker-mysql-data:/mysql-data \
           ubuntu bash -c "rm -Rf /mysql-data/tmp"
