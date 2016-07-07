FROM ubuntu:14.04

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update \
    && apt-get install -y curl nano cron \
    && curl -Lo dropbox-linux-x86_64.tar.gz https://www.dropbox.com/download?plat=lnx.x86_64 \
    && apt-get clean all

RUN mkdir -p /opt/dropbox \
    && tar xzfv dropbox-linux-x86_64.tar.gz --strip 1 -C /opt/dropbox \
    && curl -o /etc/init.d/dropbox https://gist.githubusercontent.com/thisismitch/d0133d91452585ae2adc/raw/699e7909bdae922201b8069fde3011bbf2062048/dropbox \
    && chmod +x /etc/init.d/dropbox \
    && echo "DROPBOX_USERS=\"root\"" >> /etc/default/dropbox \
    && curl -LO https://www.dropbox.com/download?dl=packages/dropbox.py \
    && chmod +x dropbox.py \
    && ln -s /opt/dropbox ~/.dropbox-dist

# set timezone
RUN echo Europe/Rome > /etc/timezone && dpkg-reconfigure --frontend noninteractive tzdata

# add utility scripts
COPY link.sh  /usr/bin/link-dropbox-client
COPY start.sh /usr/bin/start-dropbox-client
RUN chmod +x /usr/bin/link-dropbox-client
RUN chmod +x /usr/bin/start-dropbox-client
