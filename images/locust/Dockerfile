FROM ubuntu:16.04

# Let the conatiner know that there is no tty
ENV DEBIAN_FRONTEND noninteractive

# Install required packages
RUN apt-get update \
    && apt-get -y install git apt-utils nano curl apt-transport-https iputils-ping supervisor sysstat net-tools netcat \
        python python-pip python-dev ipython ipython-notebook \
    && curl -sL https://repos.influxdata.com/influxdb.key | apt-key add - \
    && echo "deb https://repos.influxdata.com/ubuntu xenial stable" | tee /etc/apt/sources.list.d/influxdb.list \
    && apt-get update \
    && apt-get -y install influxdb telegraf \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python libraries
RUN pip install --upgrade pip \
    && python -m pip install locustio --ignore-installed pyzmq

# Copy supervisor configuration
COPY supervisor.conf /etc/supervisor/conf.d/supervisor.conf

# COPY and config sysstat
COPY sysstat /etc/cron.d/sysstat
RUN sed -i.bak "s/^\([[:space:]]*ENABLED=\).*/\1\"true\"/" /etc/default/sysstat

# COPY base telegraf configuration
COPY telegraf.conf /etc/telegraf/telegraf.conf

# COPY configuration
COPY influxdb.conf /etc/influxdb/influxdb.conf

# Add git info of the current Git Repository
COPY gitinfo.sh /usr/local/bin
RUN cat /usr/local/bin/gitinfo.sh >> ~/.bashrc

# Add stats_utils
COPY stats_utils.sh /usr/local/bin/stats_utils.sh

# Add start script
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

# set terminal
ENV TERM xterm

# set the working dir
RUN mkdir -p /home/tester/
WORKDIR /home/tester/

# Expose ports
EXPOSE 8025 8083 8086 8088 8089 5557 5558

# update entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]