all: compose build-images

compose:
	# make the YAML file 'docker-compose'
	template="docker-compose-template.yml"; 														\
	generated="docker-compose.yml"; 																		\
	source config.sh;																										\
	perl -pe 's/{{(.*?)}}/$$ENV{$$1}/g' "$${template}" > $${generated};	\

build-images: build-certificates
	# build the docker images
	set -e; 													\
	current_path=$$(pwd);							\
	source config.sh;									\
	cd $${current_path}/images/mysql  \
		 && ./build_image.sh $${DOCKERHUB_REPOSITORY} $${DOCKERHUB_MYSQL_IMAGE}; \
	cd $${current_path}/images/apache \
		 && ./build_image.sh $${DOCKERHUB_REPOSITORY} $${DOCKERHUB_APACHE_IMAGE};

build-certificates:
	# build the required certificates
	source config.sh;																				\
  if [[ ! -d $${CERTS_PATH} ]]; then 											\
		mkdir -p $${CERTS_PATH};															\
		openssl req -x509 -nodes -days 365 -newkey rsa:2048 	\
							  -keyout $${CERTS_PATH}/apache.key 				\
								-out $${CERTS_PATH}/apache.crt; 					\
	fi
