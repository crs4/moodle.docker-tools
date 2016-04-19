#!/usr/bin/env bash

DOCKERHUB_REPOSITORY=${1:-"crs4"}
DOCKERHUB_IMAGE_NAME=${2:-"moodle-mysql"}

# Build MySQL image
echo "Building the MySQL image..."
docker build -t ${DOCKERHUB_REPOSITORY}/${DOCKERHUB_IMAGE_NAME} .
