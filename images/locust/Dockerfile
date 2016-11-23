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
    && apt-get -y install influxdb telegraf \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python libraries
RUN pip install --upgrade pip \
    && pip install locustio \
    && pip install ipython \
    && pip install jupyter

# Copy supervisor configuration
COPY local.conf /etc/supervisor/conf.d/local.conf
COPY master.conf /etc/supervisor/conf.d/master.conf
COPY slave.conf /etc/supervisor/conf.d/slave.conf

# COPY and config sysstat
COPY sysstat /etc/cron.d/sysstat
RUN sed -i.bak "s/^\([[:space:]]*ENABLED=\).*/\1\"true\"/" /etc/default/sysstat

# COPY base telegraf configuration
COPY telegraf.conf /etc/telegraf/telegraf.conf

# Add git info of the current Git Repository
COPY gitinfo.sh /usr/local/bin
RUN cat /usr/local/bin/gitinfo.sh >> ~/.bashrc

# Add start script
COPY start.sh /usr/local/bin/start.sh

# set terminal
ENV TERM xterm

# set the working dir
RUN mkdir -p /home/tester/
WORKDIR /home/tester/

# Expose ports
EXPOSE 8025 8083 8086 8088 8089