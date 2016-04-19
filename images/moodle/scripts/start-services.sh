#!/usr/bin/env bash

set -e

# Download Moodle and deploy it to the MOODLE_WWW_ROOT
if [[ ! "$(ls ${MOODLE_WWW_ROOT})" ]]; then
    echo "Copying Moodle ..."
    cp -r -v /opt/moodle ${WWW_ROOT}
    chown -R www-data:www-data ${WWW_ROOT}
    cat > ${WWW_ROOT}/index.html <<- EOM
<html>
    <head>
        <meta http-equiv="refresh" content="0; url=/moodle">
    </head>
<body></body>
</html>
EOM


else
    echo "Moodle folder exists..."
fi

## Start Apache2
service apache2 start

# print logs
tail -f /var/log/apache2/*