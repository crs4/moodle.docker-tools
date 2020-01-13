#!/usr/bin/env bash

# get current path
current_path="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# load configuration
source "${current_path}/config.sh"

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
