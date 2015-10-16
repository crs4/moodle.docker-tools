# omero_moodle.docker

A Dockerized Moodle for development purposes.


### Usage

 - change `config.sh` as you need
 - run `./build-images.sh`
 - run `./make-composition.sh` to build the `docker-compose.yml`
 - run `docker-compose` up -d (or `./start.sh`) to start the services
 - open your browser, go to the page `http://<YOUR_DOCKER_HOST>:4789/moodle` and follow the Moodle instructions to complete the installation
 - all moodle data will be saved on the `SHARED_HOST_FOLDER`, which can be configured on the `config.sh`.
