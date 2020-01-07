#!/usr/bin/env bash

# set the current path
current_path="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# set configuration file
config="${current_path}/config.sh"

# load configuration
source "${config}"

# help log function
function log() {
  echo -e "${@}" >&2
}

# generate the 'docker-compose' file
compose_template="docker-compose-template.yml"
compose_generated="docker-compose.yml"
log "\nGenerating '${compose_generated-compose}' file..."
envsubst < "${compose_template}" > "${compose_generated}"
log "Generating '${compose_generated-compose}' file... DONE"

#build the required certificates
log "\nGenerating certificates..."
if [[ ! -d $${CERTS_PATH} ]]; then
    mkdir -p $${CERTS_PATH} 
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
                -keyout $${CERTS_PATH}/apache.key \
                -out $${CERTS_PATH}/apache.crt; \
fi
log "Generating certificates... DONE"


# build the docker images
log "\nGenerating Docker images..."
cd "${current_path}/images/mysql" \
        && ./build_image.sh ${DOCKERHUB_REPOSITORY} ${DOCKERHUB_MYSQL_IMAGE}
cd "${current_path}/images/apache" \
        && ./build_image.sh ${DOCKERHUB_REPOSITORY} ${DOCKERHUB_APACHE_IMAGE}
cd "${current_path}/images/locust" \
        && ./build_image.sh ${DOCKERHUB_REPOSITORY} ${DOCKERHUB_LOCUST_IMAGE}
log "Generating Docker images... DONE"