#!/usr/bin/env bash

# Build Moodle image
echo "Building the Moodle image..."
docker build -t crs4/apache-php-moodle .