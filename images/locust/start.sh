#!/usr/bin/env bash

echo $1 $2 $3 $4

# parse param
MODE=${1}
WEB_APP_ADDRESS=${2//\//\\/}
LOCUST_SCRIPT=${3//\//\\/}
INIT_SCRIPT=${4}
INFLUXDB_HOSTNAME=$(hostname)

LOCUST_MODE=""
MASTER_IP=$(getent hosts master | awk '{ print $1 }')
if [[ ${MODE} == "slave" ]]; then
    HOST=$(hostname)
    LOCUST_MODE="--slave --master-host=${MASTER_IP}"
elif [[ ${MODE} == "master" ]]; then
    HOST="master"
    LOCUST_MODE="--master"
elif [[ ${MODE} == "local" ]]; then
    HOST="master"
else
    echo "Not valid parameter: ${1} !!! "
    exit -1;
fi

# set the supervisor config file
SUPERVISOR_CONF="/etc/supervisor/conf.d/${MODE}.conf"

# update telegraf config
sed -i.bak "s/^\([[:space:]]*hostname = \).*/\1\"${HOST}\"/" /etc/telegraf/telegraf.conf
# update InfluxDB server
sed -i.bak "s/\(http:\/\/\)master:8086/\1${INFLUXDB_HOSTNAME}/" /etc/telegraf/telegraf.conf

# update supervisor config
sed -i.bak "s/LOCUST_MODE/${LOCUST_MODE}/" ${SUPERVISOR_CONF}
sed -i.bak "s/LOCUST_SCRIPT/${LOCUST_SCRIPT}/" ${SUPERVISOR_CONF}
sed -i.bak "s/WEB_APP_ADDRESS/${WEB_APP_ADDRESS}/" ${SUPERVISOR_CONF}

# run the initialization script
${INIT_SCRIPT} dev

# start supervisor
/usr/bin/supervisord -n -c ${SUPERVISOR_CONF}