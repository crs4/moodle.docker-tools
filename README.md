# moodle.docker-tools

Dockerized Moodle with Omero plugins orchestrated by means of Docker Compose.


### Requirements

* [`docker`](https://docs.docker.com/install/)
* [`docker-compose`](https://docs.docker.com/compose/install/)

### Usage instructions

The `./build.sh` script allows you to easily compile all the Docker images.

Moodle and its data can be stored either on Docker volumes or on a local path of your Docker host. These and other settings can be customized by editing the `config.sh` file. You need to run the `./generate-docker-compose-file.sh` script to apply your changes to the `docker-compose.yml` configuration file.

Having the `docker-compose.yml` configuration file, you can complete the setup of your Moodle installation through the following steps:

1. type `docker-compose up -d` to start all the services. The first time you run `docker-compose` it may take some time to initiliaze the Moodle service. Type `docker-compose logs apache` to check whether the Apache server is ready:

```
apache_1  | '/opt/moodle/install-omero-modules.sh' -> '/var/www/html/moodle/install-omero-modules.sh'
apache_1  |  * Starting web server apache2
apache_1  |  *
apache_1  | ==> /var/log/apache2/access.log <==
apache_1  |
apache_1  | ==> /var/log/apache2/error.log <==
...
Command line: '/usr/sbin/apache2'
apache_1  |
```

2. open your browser at `http://<DOCKER_HOST>/moodle` (e.g., `http://localhost/moodle`) and follow the Moodle [installation procedure](docs/install.md).