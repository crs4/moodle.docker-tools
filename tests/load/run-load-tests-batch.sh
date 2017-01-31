#!/usr/bin/env bash

# current dir
CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# script to launch
SCRIPT="${CURRENT_DIR}/run-load-tests.sh"

# output filename
OUTPUT_FILE="${CURRENT_DIR}/tests.log"

# launch LOAD tests in background
nohup ${SCRIPT} > ${OUTPUT_FILE} 2>&1&

# save the process ID
TPID=$!
echo ${TPID} > "tests.pid"
echo "Tests started... PID: ${TPID}"

