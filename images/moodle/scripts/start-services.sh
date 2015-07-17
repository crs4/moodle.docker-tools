#!/usr/bin/env bash

set -e

# Download Moodle and deploy it to the MOODLE_WWW_ROOT
if [[ ! "$(ls ${MOODLE_WWW_ROOT})" ]]; then
    echo "Copying Moodle ..."
    cp -r -v /opt/moodle ${MOODLE_WWW_ROOT}
else
    echo "Moodle folder exists..."
fi

## Start Apache2
service apache2 start

# print logs
tail -f /var/log/apache2/*