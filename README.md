# omero_moodle.docker

A Dockerized Moodle for development purposes.


### Usage

 - change config.sh as you need
 - run ./make-composition.sh to build the docker-compose.yml
 - run ./build-images.sh
 - run docker-compose up -d 
 - open your browser, go to the page `http://<YOUR_DOCKER_HOST>:4789/moodle` and follow the Moodle instructions to complete the installation.
