#!/usr/bin/env bash

MODE=${1:-i}

if [[ $MODE == "-i" ]]; then
    MODE="-it --rm"
else
    MODE="-d"
fi

docker run ${MODE} \
    -p 2003:2003/udp \
    -p 8083:8083 \
    -p 8086:8086 \
    -p 8088:8088 \
    crs4/influxdb