#!/usr/bin/env bash

DOCKERHUB_REPOSITORY=${1:-"crs4"}
DOCKERHUB_IMAGE_NAME=${2:-"telegraf"}

# Build Locust image
echo "Building the Locust image..."
docker build -t ${DOCKERHUB_REPOSITORY}/${DOCKERHUB_IMAGE_NAME} .
