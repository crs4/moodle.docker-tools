#!/usr/bin/env bash

DOCKERHUB_REPOSITORY=${1:-"crs4"}
DOCKERHUB_IMAGE_NAME=${2:-"moodle-dropbox"}


# Build Moodle image
echo "Building the MoodleDocker image..."
docker build -t ${DOCKERHUB_REPOSITORY}/${DOCKERHUB_IMAGE_NAME} .
