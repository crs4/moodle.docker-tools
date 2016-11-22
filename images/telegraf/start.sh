#!/usr/bin/env bash

# set Telegraf hostname
TELEGRAF_HOSTNAME=$(hostname)

# update config filename
TELEGRAF_CONFIG_FILE="/etc/telegraf/telegraf.conf"

# set InfluxDB hostname
INFLUXDB_HOSTNAME="master"

# print usage
function print_usage(){
    echo -e "\nUsage: start [OPTIONS]"
    echo -e "\n       OPTIONS: \n"
    echo -e "\t  -h|--help               "
    echo -e "\t  --host                  hostname of the Telegraf instance (default `hostname`)"
    echo -e "\t  --apache                url of the Apche server (optional)"
    echo -e "\t  --influxdb              hostaname of the TelegrafDB instance (default 'master')"
}

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
                        # set TELEGRAF_HOSTNAME
                        --host=* )
                                TELEGRAF_HOSTNAME="${OPT#*=}"
                                shift
                                ;;
                        --host )
                                TELEGRAF_HOSTNAME="$2"
                                shift
                                ;;
                        # set APACHE_HOST
                        --apache=* )
                                APACHE_HOST="${OPT#*=}"
                                shift
                                ;;
                        --apache )
                                APACHE_HOST="$2"
                                shift
                                ;;
                        # update JUPYTER_PORT
                        --influxdb=* )
                                INFLUXDB_HOSTNAME="${OPT#*=}"
                                shift
                                ;;
                        --influxdb )
                                INFLUXDB_HOSTNAME="$2"
                                shift
                                ;;
                        -h* | --help )
                                print_usage
                                exit
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

######################################################################################################################
#### update telegraf config
######################################################################################################################
# 1) TELEGRAF Hostname
sed -i.bak "s/^\([[:space:]]*hostname = \).*/\1\"${TELEGRAF_HOSTNAME}\"/" /etc/telegraf/telegraf.conf
# 2) InfluxDB server
sed -i.bak "s/\(http:\/\/\)master\(:8086\)/\1${INFLUXDB_HOSTNAME}\2/" /etc/telegraf/telegraf.conf
# 3) Apache server
if [[ -n ${APACHE_HOST} ]]; then
    sed -i.bak "s/^#\([[inputs.apache]]\)/\1/" /etc/telegraf/telegraf.conf
    sed -i.bak "s/^#apache_urls/    urls/" /etc/telegraf/telegraf.conf
    sed -i.bak "s/\(http:\/\/\)localhost\/\(server-status?auto\)/\1${APACHE_HOST}\2/" /etc/telegraf/telegraf.conf
fi
######################################################################################################################

echo "Settings...."
echo "Telegraf host: '${TELEGRAF_HOSTNAME}'"
echo "Influxdb host: '${INFLUXDB_HOSTNAME}'"

# start telegraf
/usr/bin/telegraf -config /etc/telegraf/telegraf.conf -config-directory /etc/telegraf/telegraf.d