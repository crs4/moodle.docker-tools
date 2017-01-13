#!/usr/bin/env bash

set -e

IMAGE_NAME="crs4/locust"
WEB_APP_ADDRESS="http://omero-test.crs4.it/moodle"
LOCUST_SCRIPT="/home/tester/docker-tools/tests/load/locust_scripts/tests.py"
SETUP_SCRIPT="../../tests/load/load-test-setup.sh"

# default TEST
DATASET="../../tests/datasets/dev"

# default mode
MODE="--rm"

# default docker container name
DOCKER_CONTAINER_HOSTNAME="$(hostname)-docker"

# default volume
NO_VOLUME="false"
VOLUME_NAME="locust-influxdb-data"

# default output folder
OUTPUT_FOLDER="results"

# parse arguments
while [ -n "$1" ]; do
        # Copy so we can modify it (can't modify $1)
        OPT="$1"
        # Detect argument termination
        if [ x"$OPT" = x"--" ]; then
                shift
                for OPT ; do
                        OTHER_OPTS="$OTHER_OPTS \"$OPT\""
                done
                break
        fi
        # Parse current opt
        while [ x"$OPT" != x"-" ] ; do
                case "$OPT" in
                        # set interactive MODE
                        -i | --interactive )
                                MODE="-it --rm"
                                ;;
                        # set daemon MODE
                        -d | --daemon )
                                MODE="-d"
                                ;;
                        # dataset folder
                        -o | --output )
                                OUTPUT_FOLDER="$2"
                                shift
                                ;;
                        -o=* | --output=* )
                                OUTPUT_FOLDER="${OPT#*=}"
                                shift
                                ;;
                        # dataset folder
                        --config )
                                CONFIG_FILE="$2"
                                shift
                                ;;
                        --config=* )
                                CONFIG_FILE="${OPT#*=}"
                                shift
                                ;;
                        # dataset folder
                        --dataset )
                                DATASET="$2"
                                shift
                                ;;
                        --dataset=* )
                                DATASET="${OPT#*=}"
                                shift
                                ;;
                        # stats conf
                        --stats-conf=* )
                                STATS_CONF="${OPT#*=}"
                                shift
                                ;;
                        --stats-conf )
                                STATS_CONF="$2"
                                shift
                                ;;
                        # set web app
                        -l=* | --locust-script=* )
                                LOCUST_SCRIPT="${OPT#*=}"
                                shift
                                ;;
                        -l | --locust-script )
                                LOCUST_SCRIPT="$2"
                                shift
                                ;;
                        # set web app
                        -w=* | --web-app=* )
                                WEB_APP_ADDRESS="${OPT#*=}"
                                shift
                                ;;
                        -w | --web-app )
                                WEB_APP_ADDRESS="$2"
                                shift
                                ;;
                        # setup script
                        -s=* | --setup-script=* )
                                SETUP_SCRIPT="${OPT#*=}"
                                shift
                                ;;
                        -s | --setup-script )
                                SETUP_SCRIPT="$2"
                                shift
                                ;;
                        # volume name
                        -v | --volume )
                                VOLUME_NAME="$2"
                                shift
                                ;;
                        -v=* | --volume=* )
                                VOLUME_NAME="${OPT#*=}"
                                shift
                                ;;
                        --no-volume )
                                NO_VOLUME="true"
                                ;;
                        # Anything unknown is recorded for later
                        * )
                                OTHER_OPTS="$OTHER_OPTS $OPT"
                                break
                                ;;
                esac
                # Check for multiple short options
                # NOTICE: be sure to update this pattern to match valid options
                NEXTOPT="${OPT#-[cfr]}" # try removing single short opt
                if [ x"$OPT" != x"$NEXTOPT" ] ; then
                        OPT="-$NEXTOPT"  # multiple short opts, keep going
                else
                        break  # long form, exit inner loop
                fi
        done
        # move to the next param
        shift
done


VOLUME_OPTS=""
if [[ ${NO_VOLUME} == "false" ]]; then
    VOLUME_OPTS="-v ${VOLUME_NAME}:/var/lib/influxdb"
fi

ENV_CONFIG_FILE=""
if [[ -n ${CONFIG_FILE} ]]; then
    filename=$(basename ${CONFIG_FILE})
    ENV_CONFIG_FILE="-e CYTEST_CONFIGURATION_FILE=\"/config/${filename}\""
    CONFIG_LOCAL_PATH="$( cd "$( dirname ${CONFIG_FILE} )" && pwd )"
    VOLUME_OPTS="-v ${CONFIG_LOCAL_PATH}:/config ${VOLUME_OPTS}"
fi

if [[ -n ${STATS_CONF} ]]; then
    STATS_CONF_PATH="$( cd "$( dirname ${STATS_CONF} )" && pwd )"
    VOLUME_OPTS="-v ${STATS_CONF_PATH}:/stats ${VOLUME_OPTS}"
    OTHER_OPTS="--stats-conf /stats/$(basename ${STATS_CONF}) ${OTHER_OPTS}"
fi

#
if [[ ! -f ${SETUP_SCRIPT} ]]; then
    echo "Script '${SETUP_SCRIPT}' doesn't exist!"
    exit -1
fi
SETUP_SCRIPT_FOLDER="$( cd "$( dirname "${SETUP_SCRIPT}" )" && pwd )"
SETUP_SCRIPT=$(basename ${SETUP_SCRIPT})

#
if [[ ! -d ${DATASET} ]]; then
    echo "Directory '${DATASET}' doesn't exist!"
    exit -1
fi
DATASET_FOLDER="$( cd ${DATASET} && pwd )"
DATASET=$(basename ${DATASET})

# output folder initialization
mkdir -p ${OUTPUT_FOLDER}
OUTPUT_FOLDER="$( cd ${OUTPUT_FOLDER} && pwd )"

echo -e "Configuration..."
echo -e " - Mode: ${MODE}"
echo -e " - Volume name: ${VOLUME_NAME}"
echo -e " - Volume disabled: ${NO_VOLUME}"
echo -e " - Locust options: ${OTHER_OPTS}"
echo -e " - WebApp address: ${WEB_APP_ADDRESS}"
echo -e " - Setup script: ${SETUP_SCRIPT}"
echo -e " - Setup script path: ${SETUP_SCRIPT_FOLDER}"
echo -e " - Dataset: ${DATASET}"
echo -e " - Dataset path: ${DATASET_FOLDER}"
echo -e " - Output path: ${OUTPUT_FOLDER}"
echo -e " - Default config file: ${CONFIG_FILE}"
echo -e "\n"

docker run ${MODE} ${VOLUME_OPTS} \
    -v ${DATASET_FOLDER}:"/dataset" \
    -v ${SETUP_SCRIPT_FOLDER}:"/scripts" \
    -v ${OUTPUT_FOLDER}:"/results" \
    -h ${DOCKER_CONTAINER_HOSTNAME} \
    -p "18086:8086"  \
    -p "18083:8083"  \
    -p "18088:8088"  \
    -p "18089:8089"  \
    -p "18090:10000" \
    ${IMAGE_NAME} \
    -w ${WEB_APP_ADDRESS} -f ${LOCUST_SCRIPT} ${OTHER_OPTS} \
    -s "/scripts/${SETUP_SCRIPT}" "/dataset"
