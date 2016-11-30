#!/usr/bin/env bash

# function to collect locust stats
function collect_locust_stats(){
    local locust_server_url="${1}"
    local output_file_prefix="${2}"
    echo "${locust_server_url}/stats/requests/csv"
    curl -o "${output_file_prefix}.csv" -G "${locust_server_url}/stats/requests/csv"
}

# function to collect influxdb stats
function collect_output(){
    local influxdb_server_url="${1}"
    local output_file_prefix="${2}"
    local info="${3}"
    local start_time="${4/@/ }"
    local end_time="${5/@/ }"
    echo "START: ${start_time}"
    echo "END: ${end_time}"
    influxdb_endpoint="${influxdb_server_url}/query?pretty=true"
    curl -o "${output_file_prefix}-${info}.json" \
        -G ${influxdb_endpoint} \
        --data-urlencode "db=telegraf" \
        --data-urlencode "q=SELECT * FROM \"${info}\" WHERE \"time\">'${start_time}' AND \"time\"<'${end_time}'"
}

# function to collect stats
function collect_outputs(){
    local locust_server_url="${1}"
    local influxdb_server_url="${2}"
    local output_file_prefix="${3}"
    local start_time="${4}"
    local end_time="${5}"
    # collect locust stats
    collect_locust_stats ${locust_server_url} ${output_file_prefix}
    # collect stats from influxdb
    host_info=("cpu" "disk" "diskio" "inode" "io" "mem" "network" "processes" "apache")
    for info in "${host_info[@]}"
    do
        collect_output ${influxdb_server_url} ${output_file_prefix} ${info} ${start_time} ${end_time}
    done;
}