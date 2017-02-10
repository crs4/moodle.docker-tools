#!/usr/bin/env bash

# default mode
MODE="-it --rm"

# default volume
VOLUME_NAME="influxdb-data"

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
                        -v | --volume )
                                VOLUME_NAME="$2"
                                shift
                                ;;
                        # set APACHE_HOST
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
if [[ -z ${NO_VOLUME} ]]; then
    VOLUME_OPTS="-v ${VOLUME_NAME}:/var/lib/influxdb"
fi

docker run ${MODE} ${VOLUME_OPTS} \
    -p 2003:2003/udp \
    -p 8083:8083 \
    -p 8086:8086 \
    -p 8088:8088 \
    crs4/influxdb