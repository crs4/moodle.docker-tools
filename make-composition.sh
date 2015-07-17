#!/usr/bin/env bash

# docker-compose template: contains {{ ... }} for env vars
template="docker-compose-template.yml"
# docker-compose file: all env var are resolved
generated="docker-compose.yml"

# load env
source config.sh

# perform substitution and generate the docker-compose file
perl -pe 's/{{(.*?)}}/$ENV{$1}/g' "${template}" > ${generated}

