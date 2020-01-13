#!/usr/bin/env bash

DOCKERHUB_REPOSITORY=${1:-"crs4"}
DOCKERHUB_IMAGE_NAME=${2:-"moodle-init"}

# Build Moodle image
echo "Building the Moodle image..."
docker build -t ${DOCKERHUB_REPOSITORY}/${DOCKERHUB_IMAGE_NAME} .
