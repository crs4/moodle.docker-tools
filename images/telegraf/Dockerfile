FROM ubuntu:16.04

# Let the conatiner know that there is no tty
ENV DEBIAN_FRONTEND noninteractive

# Install required packages
RUN apt-get update \
    && apt-get -y install git apt-utils nano curl apt-transport-https iputils-ping supervisor sysstat net-tools \
    && curl -sL https://repos.influxdata.com/influxdb.key | apt-key add - \
    && echo "deb https://repos.influxdata.com/ubuntu xenial stable" | tee /etc/apt/sources.list.d/influxdb.list \
    && apt-get update \
    && apt-get -y install telegraf \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# COPY and config sysstat
COPY sysstat /etc/cron.d/sysstat
RUN sed -i.bak "s/^\([[:space:]]*ENABLED=\).*/\1\"true\"/" /etc/default/sysstat

# COPY base telegraf configuration
COPY telegraf.conf.orig /etc/telegraf/telegraf.conf

# Add git info of the current Git Repository
COPY gitinfo.sh /usr/local/bin
RUN cat /usr/local/bin/gitinfo.sh >> ~/.bashrc

# add entrypoint script
ADD start.sh /usr/local/bin/start

# set terminal
ENV TERM xterm

# Expose ports
EXPOSE 8025 8083 8086 8088 8089

# entrypoint
ENTRYPOINT ["/usr/local/bin/start"]