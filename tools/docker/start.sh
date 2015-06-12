#!/usr/bin/env bash

# Global settings
CONTAINER_NAME="moodle_ome"
BASEDIR="$(pwd)/Sharing"
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


function wait_for_ssh {
    SSH_EXIT_STATUS=255
    while [[ $SSH_EXIT_STATUS -eq 255 ]];do
        ssh ${CONTAINER_SSH_PORT} root@${DOCKER_HOST_IP} echo "" &> /dev/null
        sleep 1
        SSH_EXIT_STATUS=$?
    done
}

# Check whehter the Shared Moodle Folders exist
if [[ -d "${WWW_DIR}/moodle" ]]; then
    echo "Shared Moodle exists @ ${WWW_DIR}"
else
    # start a temp container
    echo "Initializing Moodle (@${MOODLE_WWW}..."
    docker run -d -p ${CONTAINER_SSH_PORT}:22 -p 4789:80 --name ${CONTAINER_NAME} moodle
    # Wait for ssh
    wait_for_ssh

    echo "Copying key..."
    cat ~/.ssh/id_dsa.pub | ssh -p ${CONTAINER_SSH_PORT} root@${DOCKER_HOST_IP} "cat > .ssh/authorized_keys"

    # copy directories to the shared folders
    if [[ ! -d "${MOODLE_WWW}" ]]; then
        scp -r -P${CONTAINER_SSH_PORT} root@${DOCKER_HOST_IP}:/var/www/html/moodle ${MOODLE_WWW}
        scp -r -P${CONTAINER_SSH_PORT} root@${DOCKER_HOST_IP}:/data/moodle ${MOODLE_DATA}
        scp -r -P${CONTAINER_SSH_PORT} root@${DOCKER_HOST_IP}:/var/lib/mysql/mysql ${MYSQL_DATA_DIR}

        chmod -R 777 ${MYSQL_DATA_DIR}
    fi

    # kill the temp container
    docker rm -f ${CONTAINER_NAME}
fi


# Start the container
docker run -d -p ${CONTAINER_SSH_PORT}:22 -p 4789:80 \
    -v ${WWW_DIR}:/var/www/html -v ${DATA_DIR}:/data \
    -v ${MOODLE_DATA}:/data/moodle \
    -v ${MYSQL_DATA_DIR}:/var/lib/mysql \
    --name ${CONTAINER_NAME} moodle

# Wait for ssh
wait_for_ssh

echo "Copying key..."
cat ~/.ssh/id_dsa.pub | ssh -p ${CONTAINER_SSH_PORT} root@${DOCKER_HOST_IP} "cat > .ssh/authorized_keys"

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

