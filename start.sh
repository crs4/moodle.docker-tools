#!/usr/bin/env bash

if [[ "$@" -eq 1 ]]; then
	BASEDIR="$1"
elif [[ -n ${BASE_MOODLE_DOCKER_DIR} ]]; then
	BASEDIR=${BASE_MOODLE_DOCKER_DIR}
else
	BASEDIR="${HOME}/Sharing/MoodleDocker"
fi

# Global settings
BASE_MOODLE_DOCKER_DIR=${BASE_DIR}
CONTAINER_NAME="moodle_ome"
WWW_DIR="${BASEDIR}/www"
DATA_DIR="${BASEDIR}/data"
CONTAINER_SSH_PORT=4376

# MySQL settings
MYSQL_DATA_DIR=${DATA_DIR}/mysql

# Moodle Settings
MOODLE_WWW="${WWW_DIR}/moodle"
MOODLE_VERSION=MOODLE_29_STABLE
MOODLE_ARCHIVES="${BASEDIR}/dist"
MOODLE_DATA=${DATA_DIR}/moodledata


# make dirs
mkdir -p ${WWW_DIR}
mkdir -p ${DATA_DIR}
mkdir -p ${MOODLE_DATA}
mkdir -p ${MYSQL_DATA_DIR}

# env to export
export BASE_MOODLE_DOCKER_DIR
export MOODLE_WWW
export MOODLE_DATA

# utility function
function wait_for_ssh {
    SSH_EXIT_STATUS=255
    while [[ $SSH_EXIT_STATUS -eq 255 ]];do
        ssh ${CONTAINER_SSH_PORT} root@${DOCKER_HOST_IP} echo "" &> /dev/null
        sleep 1
        SSH_EXIT_STATUS=$?
    done
}

# SSH key
SSH_KEY="${HOME}/.ssh/id_dsa.pub"
if [[ ! -f ${SSH_KEY} ]]; then
	SSH_KEY="${HOME}/.ssh/id_rsa.pub"
fi

# Determine the DOCKER_HOST_IP from the DOCKER_HOST env var:
# if no DOCKER_HOST is setted, 0.0.0.0 is assumed as DOCKER_HOST_IP
if [[ -n ${DOCKER_HOST} ]]; then
	DOCKER_HOST_IP=$(echo ${DOCKER_HOST} | grep -E -o "([0-9]+\.)+[0-9]+")
else
	DOCKER_HOST_IP=0.0.0.0
fi

# Check whehter the Shared Moodle Folders exist
if [[ -d "${WWW_DIR}/moodle" ]]; then
    echo "Shared Moodle exists @ ${WWW_DIR}"
else
    # start a temp container
    echo "Initializing Moodle (@${MOODLE_WWW}..."
    docker run -d -p ${CONTAINER_SSH_PORT}:22 -p 4789:80 \
			-v ${MYSQL_DATA_DIR}:/var/lib/mysql \
			--name ${CONTAINER_NAME} moodle
    # Wait for ssh
    wait_for_ssh

    echo "Copying key..."
    cat ${SSH_KEY} | ssh -p ${CONTAINER_SSH_PORT} root@${DOCKER_HOST_IP} "cat >> .ssh/authorized_keys"

    # copy directories to the shared folders
    if [[ ! -d "${MOODLE_WWW}" ]]; then
        scp -r -P${CONTAINER_SSH_PORT} root@${DOCKER_HOST_IP}:/opt/moodle ${MOODLE_WWW}
        scp -r -P${CONTAINER_SSH_PORT} root@${DOCKER_HOST_IP}:/data/moodle ${MOODLE_DATA}

        # Initialize the MySQL DB
        ssh -p ${CONTAINER_SSH_PORT} root@${DOCKER_HOST_IP} "/usr/bin/mysql_install_db"
    fi

    # kill the temp container
    docker rm -f ${CONTAINER_NAME}
fi


# Start the container
docker run -d -p ${CONTAINER_SSH_PORT}:22 -p 4789:80 -p 4306:3306 \
    -v ${WWW_DIR}:/var/www/html -v ${DATA_DIR}:/data \
    -v ${MOODLE_DATA}:/data/moodle \
    -v ${MYSQL_DATA_DIR}:/var/lib/mysql \
    --name ${CONTAINER_NAME} moodle

# Wait for ssh
wait_for_ssh

echo "Copying key..."
cat ${SSH_KEY} | ssh -p ${CONTAINER_SSH_PORT} root@${DOCKER_HOST_IP} "cat >> .ssh/authorized_keys"

# get the IP address
CONTAINER_ADDRESS=$(docker inspect --format '{{ .NetworkSettings.IPAddress }}' ${CONTAINER_NAME})
echo IP Address of the Moodle container: $CONTAINER_ADDRESS

# Start Apache2 and MySQL
echo "Starting services..."
ssh -p ${CONTAINER_SSH_PORT} root@${DOCKER_HOST_IP} start-services

# Check whether the Moodle DB exists
if [[ -z $(ssh -p ${CONTAINER_SSH_PORT} root@${DOCKER_HOST_IP} 'mysql -e  "SHOW DATABASES" | grep moodle') ]]; then
    echo "Initializing MySQL DB for moodle..."
    ssh -p ${CONTAINER_SSH_PORT} root@${DOCKER_HOST_IP} "mysql < /tmp/moodle.sql"
fi

