#!/usr/bin/env bash

# function to collect locust stats
function collect_locust_stats(){
    local test_name="${1}"
    curl -o "${OUTPUT_FOLDER}/${test_name}.csv" "http://localhost:8086/stats/requests/csv"
}

# function to collect influxdb stats
function collect_output(){
    local test_name="${1}"
    local info="${2}"
    influxdb_endpoint="http://localhost:8086/query?pretty=true"
    curl -o "${OUTPUT_FOLDER}/${test_name}-${info}.json" \
        -G ${influxdb_endpoint} \
        --data-urlencode "db=telegraf" \
        --data-urlencode "q=SELECT * FROM \"${info}\" WHERE \"time\">'${start_time}' AND \"time\"<'${end_time}'"
}

# function to collect stats
function collect_outputs(){
    local test_name="${1}"
    # collect locust stats
    collect_locust_stats ${test_name}
    # collect stats from influxdb
    host_info=("cpu" "disk" "diskio" "inode" "io" "mem" "network" "processes")
    for info in "${host_info[@]}"
    do
        collect_output ${test_name} ${info}
    done;
}