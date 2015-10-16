#!/usr/bin/env bash

# Images to build
images=("mysql moodle")

# Path of images
images_path="$(pwd)/images"

# Build images
for image in ${images[@]}; do
	cd "${images_path}/${image}"
	"./build_image.sh"
done