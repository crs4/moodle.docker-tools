# omero_moodle.docker

Moodle Dockerization (for development).


### Usage

 - change config.sh if you need
 - run ./make-composition.sh to build the docker-compose.yml
 - run ./build-images.sh
 - run docker-compose up -d 
 - open a web browser at http://<YOUR_DOCKER_HOST>:4789/moodle and complete the Moodle installation following the instructions.
