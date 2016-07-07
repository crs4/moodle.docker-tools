#!/bin/bash

if [[ -f config.sh ]]; then
  source config.sh
fi;

MYSQL_DUMP=$1

if [[ ! -f ${MYSQL_DUMP} ]]; then
  echo "${MYSQL_DUMP} doesn't exist!!!";
  exit -1;
fi

mysqladmin -u root -p${MYSQL_ROOT_PASSWORD} drop ${MYSQL_DATABASE}
mysqladmin -u root -p${MYSQL_ROOT_PASSWORD} create ${MYSQL_DATABASE}

mysql -u root -p${MYSQL_ROOT_PASSWORD} ${MYSQL_DATABASE} \
      -e "GRANT ALL PRIVILEGES ON ${MYSQL_DATABASE}.* TO '${MYSQL_USER}'@'*' WITH GRANT OPTION;"

mysql -u root -p${MYSQL_ROOT_PASSWORD} ${MYSQL_DATABASE} < ${MYSQL_DUMP}
