# omero_moodle.docker

A Dockerized Moodle for development purposes.


### Usage

 - change `config.sh` as you need
 - run `make` to build docker images and the docker-compose configuration file
 - run `docker-compose` up -d (or `./start.sh`) to start the services
 - open your browser, go to the page `http://<YOUR_DOCKER_HOST>/moodle` and follow the Moodle instructions to complete the installation
 - all moodle data will be saved on shared host folders or docker volumes, accordingly to your configuration settings in `config.sh`
 - after installing Moodle, you can use the script `install-modules.sh` to install all CRS4's plugins for Moodle.
