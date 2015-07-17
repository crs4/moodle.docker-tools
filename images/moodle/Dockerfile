FROM ubuntu:14.04


# Let the conatiner know that there is no tty
ENV DEBIAN_FRONTEND noninteractive

# Update
RUN apt-get update

# Install Apache/MySQL/PHP
RUN apt-get -y install apache2 mysql-client mysql-server php5 git-core
RUN echo "ServerName localhost" >>  /etc/apache2/apache2.conf

# Install Additional Software
RUN apt-get -y install graphviz aspell php5-pspell php5-curl php5-gd php5-intl php5-mysql php5-xmlrpc php5-ldap clamav


### SSH installation and settings ###
RUN apt-get update && apt-get install -y openssh-server
RUN mkdir /var/run/sshd
RUN echo 'root:moodle' | chpasswd
RUN sed -i 's/PermitRootLogin without-password/PermitRootLogin yes/' /etc/ssh/sshd_config

RUN sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd
ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

# copy the public key of the current user
RUN mkdir -p /root/.ssh

### Moodle Settings ###

# Env for Moodle
ENV MOODLE_VERSION MOODLE_29_STABLE
ENV MOODLE_WWW_ROOT /var/www/html/moodle
ENV MOODLE_DATA_DIR /data/moodle

# Downloads MOODLE
RUN cd /opt && git clone git://git.moodle.org/moodle.git && cd moodle && git checkout ${MOODLE_VERSION}
RUN cp -a /opt/moodle ${MOODLE_WWW_ROOT}

# Init Moodle dirs
RUN mkdir -p ${MOODLE_DATA_DIR}
RUN chown -R www-data ${MOODLE_DATA_DIR}
RUN chmod -R 777 ${MOODLE_DATA_DIR}
RUN chmod -R 0755 ${MOODLE_WWW_ROOT}


### MYSQL settings ###

# MySQL DataConfig
ENV MYSQL_DATA_DIR /data/mysql

# Updates MySQL configuration
RUN sed -i -e"s/^bind-address\s*=\s*127.0.0.1/bind-address = 0.0.0.0/" /etc/mysql/my.cnf
RUN sed -i -e"s/^default_storage_engine.*/default_storage_engine = innodb/" /etc/mysql/my.cnf
RUN sed -i -e"s/^innodb_file_per_table.*/innodb_file_per_table = 1/" /etc/mysql/my.cnf
RUN sed -i -e"s/^innodb_file_format.*/innodb_file_format = Barracuda/" /etc/mysql/my.cnf

# Adds for intializing MySQL tables for Moodle
ADD scripts/moodle.sql /tmp/moodle.sql


### Global scripts ###
ADD scripts/start-services.sh /usr/local/bin/start-services
RUN chmod +x /usr/local/bin/start-services

### PORTS to expose ###
EXPOSE 22 80 3306

# entrypoint
ENTRYPOINT ["/usr/sbin/sshd", "-D"]