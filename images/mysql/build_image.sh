#!/usr/bin/env bash

# Build MySQL image
echo "Building the MySQL image..."
docker build -t crs4/mysql-moodle .