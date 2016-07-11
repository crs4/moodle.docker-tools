#!/usr/bin/env bash

# the path of this script
CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# set the filename
FILENAME="questions.csv"
if [[ -n $1 ]]; then
    FILENAME=${1}
fi

# load default settings
source ${CURRENT_DIR}/../../config.sh

# dump the list of multichoice questions to the file ${FILENAME}
mysql -h ${MYSQL_HOST} -u ${MYSQL_USER} -p${MYSQL_PASSWORD}  \
      -e "SELECT id, qtype FROM mdl_question WHERE qtype='omeromultichoice'" \
      ${MYSQL_DATABASE} > "multichoice-${FILENAME}"

# dump the list of interactive questions to the file ${FILENAME}
mysql -h ${MYSQL_HOST} -u ${MYSQL_USER} -p${MYSQL_PASSWORD}  \
      -e "SELECT id, qtype FROM mdl_question WHERE qtype='omerointeractive'" \
      ${MYSQL_DATABASE} > "interactive-${FILENAME}"