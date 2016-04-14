#!/bin/sh

CERTS_PATH=images/moodle/certs

mkdir -p ${CERTS_PATH}
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ${CERTS_PATH}/apache.key -out ${CERTS_PATH}/apache.crt
