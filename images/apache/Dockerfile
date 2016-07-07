FROM ubuntu:14.04

# Let the conatiner know that there is no tty
ENV DEBIAN_FRONTEND noninteractive

# Update
RUN apt-get update

# Install Apache/MySQL/PHP and additional Software
RUN apt-get update \
    && apt-get -y install \
       apache2 mysql-client php5 git-core nodejs-legacy npm \
       graphviz aspell php5-pspell \
       php5-curl php5-gd php5-intl php5-mysql php5-xmlrpc php5-ldap clamav \
    && apt-get clean

# update apache configuration
RUN echo "ServerName localhost" >>  /etc/apache2/apache2.conf

# Install GRUNT plugins
RUN npm install -g grunt-cli

# Update the PHP.ini file, enable <? ?> tags and quieten logging.
RUN sed -i "s/error_reporting = .*$/error_reporting = E_ERROR | E_WARNING | E_PARSE/" /etc/php5/apache2/php.ini

# Path of the apache WWW root
ENV WWW_ROOT /var/www/html

# enable HTTPS
RUN a2enmod ssl
RUN a2ensite default-ssl.conf

# copy certificates
COPY certs/apache.key /etc/apache2/ssl/apache.key
COPY certs/apache.crt /etc/apache2/ssl/apache.crt

### Moodle Download and Setting ###

# Moodle Env
ENV MOODLE_VERSION MOODLE_29_STABLE
ENV MOODLE_WWW_ROOT ${WWW_ROOT}/moodle
ENV MOODLE_DATA_DIR /var/www/moodledata

# Clone Moodle
COPY moodle /opt/moodle
RUN cd /opt/moodle \
    && git checkout ${MOODLE_VERSION}

# download grunt requirements
RUN cd /opt/moodle \
  && npm install grunt --save-dev \
  && npm install grunt-contrib-uglify --save-dev \
  && npm install grunt-contrib-jshint --save-dev \
  && npm install grunt-contrib-less --save-dev \
  && npm install grunt-contrib-watch --save-dev \
  && npm install shifter --save-dev

# set user permissions
RUN usermod -u 1000 www-data

# Init Moodle dirs
RUN mkdir -p ${MOODLE_DATA_DIR}
RUN chown -R www-data ${MOODLE_DATA_DIR}
RUN chmod -R 777 ${MOODLE_DATA_DIR}

### Global scripts ###
ADD scripts/start-services.sh /usr/local/bin/start-services
RUN chmod +x /usr/local/bin/start-services

# set timezone
RUN echo Europe/Rome > /etc/timezone && dpkg-reconfigure --frontend noninteractive tzdata

# Set VOLUMEs to persist MOODLE instance and its data
VOLUME ${WWW_ROOT}
VOLUME ${MOODLE_DATA_DIR}

### PORTS to expose ###
EXPOSE 80 443

### ENTRYPOINT ##
CMD ["start-services"]
