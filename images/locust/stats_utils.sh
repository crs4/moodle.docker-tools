#!/usr/bin/env bash

# function to collect locust stats
function collect_locust_stats(){
    local locust_server_url="${1}"
    local output_file_prefix="${2}"
    echo "${locust_server_url}/stats/requests/csv"
    curl -o "${output_file_prefix}.csv" -G "${locust_server_url}/stats/requests/csv"
}

# function to collect influxdb stats
function collect_stat(){
    local influxdb_server_url="${1}"
    local output_file_prefix="${2}"
    local info="${3}"
    local start_time="${4/@/ }"
    local end_time="${5/@/ }"
    echo "Getting '${info}' stats ..."
    echo "START: ${start_time}"
    echo "END: ${end_time}"
    influxdb_endpoint="${influxdb_server_url}/query?pretty=true"
    curl -o "${output_file_prefix}-${info}.json" \
        -G ${influxdb_endpoint} \
        --data-urlencode "db=telegraf" \
        --data-urlencode "q=SELECT * FROM \"${info}\" WHERE \"time\">'${start_time}' AND \"time\"<'${end_time}'"
}

# function to collect stats
function collect_stats(){
    local influxdb_server_url="${1}"
    local output_file_prefix="${2}"
    local start_time="${3}"
    local end_time="${4}"
    local config="${5}"

    # collect influxdb stats
    if [[ -z ${config} ]]; then
        echo -e "\nWARNING: no config file to collect stats!\n"
    elif [[ -f ${config} ]]; then
        while IFS='\n' read -r line || [[ -n "$line" ]]; do
            echo -e "\nList of fields: $line"
            if [[ ${line} != "#*" ]]; then
                info=(${line})
                for info in "${info[@]}"
                do
                    collect_stat ${influxdb_server_url} ${output_file_prefix} ${info} ${start_time} ${end_time}
                done;
            fi
        done < "${config}"
    else
        echo -e "ERROR: file '$config' doesn't exist!"
    fi
}