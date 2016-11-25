#!/usr/bin/env bash

IMAGE_NAME="crs4/locust"
WEB_APP_ADDRESS="http://omero-test.crs4.it/moodle"
LOCUST_SCRIPT="/home/tester/docker-tools/tests/load/locust_scripts/tests.py"
INIT_SCRIPT="/scripts/test-setup.sh"

# default TEST
TEST="dev"
#
DATASET_FOLDER="$(pwd)/../datasets"
#
SETUP_SCRIPT_FOLDER="$(pwd)/../docker"

# default mode
MODE="-it --rm"

# default volume
VOLUME_NAME="locust-influxdb-data"

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
                        # volume name
                        -t | --test )
                                TEST="$2"
                                shift
                                ;;
                        -t=* | --test=* )
                                TEST="${OPT#*=}"
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
if [[ -z ${NO_VOLUME} ]]; then
    VOLUME_OPTS="-v ${VOLUME_NAME}:/var/lib/influxdb"
fi


docker run ${MODE}  \
    -v ${DATASET_FOLDER}:"/datasets" \
    -v ${SETUP_SCRIPT_FOLDER}:"/scripts" \
    -p "18086:8086"  \
    -p "18083:8083"  \
    -p "18088:8088"  \
    -p "18089:8089"  \
    -p "18090:10000" \
    ${IMAGE_NAME} \
    -w ${WEB_APP_ADDRESS} -f ${LOCUST_SCRIPT} -s ${INIT_SCRIPT} ${TEST}
