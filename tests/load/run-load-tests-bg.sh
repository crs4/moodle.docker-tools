#!/usr/bin/env bash

nohup ./run-load-tests.sh &
echo "$!" > $(date +'%Y-%m-%d@%H:%M:%S').pid