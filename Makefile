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
	images=("mysql moodle"); 					\
	images_path="$$(pwd)/images"; 		\
	for image in $${images[@]}; do		\
		cd "$${images_path}/$${image}"; \
		"./build_image.sh"; 						\
	done;

build-certificates:
	# build the required certificates
	source config.sh;																				\
  if [[ ! -d $${CERTS_PATH} ]]; then 											\
		mkdir -p $${CERTS_PATH};															\
		openssl req -x509 -nodes -days 365 -newkey rsa:2048 	\
							  -keyout $${CERTS_PATH}/apache.key 				\
								-out $${CERTS_PATH}/apache.crt; 					\
	fi
