FROM ubuntu:16.04

# Let the conatiner know that there is no tty
ENV DEBIAN_FRONTEND noninteractive

# Install required packages
RUN apt-get update \
    && apt-get -y install git apt-utils nano curl apt-transport-https iputils-ping supervisor sysstat net-tools \
        python python-pip python-dev ipython ipython-notebook \
    && curl -sL https://repos.influxdata.com/influxdb.key | apt-key add - \
    && echo "deb https://repos.influxdata.com/ubuntu xenial stable" | tee /etc/apt/sources.list.d/influxdb.list \
    && apt-get update \
    && apt-get -y install influxdb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# COPY and config sysstat
COPY sysstat /etc/cron.d/sysstat
RUN sed -i.bak "s/^\([[:space:]]*ENABLED=\).*/\1\"true\"/" /etc/default/sysstat

# Add git info of the current Git Repository
COPY gitinfo.sh /usr/local/bin
RUN cat /usr/local/bin/gitinfo.sh >> ~/.bashrc

# COPY configuration
COPY influxdb.conf /etc/influxdb/influxdb.conf

# set terminal
ENV TERM xterm

# Expose ports
EXPOSE 2003 8083 8086 8088

# entrypoint
ENTRYPOINT ["influxd", "-config", "/etc/influxdb/influxdb.conf"]
