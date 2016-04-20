FROM mysql:5.6

# MYSQL_DATADIR
ENV MYSQL_DATADIR /var/lib/mysql

# Add custom configuration file
ADD conf/my.cnf /etc/mysql/conf.d/my.cnf

# Set MYSQL_DATADIR volume
VOLUME ${MYSQL_DATADIR}
