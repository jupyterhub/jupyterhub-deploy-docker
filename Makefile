include .env

.DEFAULT_GOAL=build

network:
	@docker network inspect $(DOCKER_NETWORK_NAME) >/dev/null 2>&1 || docker network create $(DOCKER_NETWORK_NAME)

volumes:
	@docker volume inspect $(DATA_VOLUME_HOST) >/dev/null 2>&1 || docker volume create --name $(DATA_VOLUME_HOST)

self-signed-cert:
	# make a self-signed cert

secrets/jupyterhub.crt:
	@if [ "${SECRETS_VOLUME}" = "" ]; then \
		echo "Need an SSL certificate in secrets/jupyterhub.crt"; \
		exit 1; \
	fi

secrets/jupyterhub.key:
	@if [ "${SECRETS_VOLUME}" = "" ]; then \
		echo "Need an SSL key in secrets/jupyterhub.key"; \
		exit 1; \
	fi

userlist:
	@echo "Add usernames, one per line, to ./userlist, such as:"
	@echo "    zoe admin"
	@echo "    wash"
	@exit 1

check-files: secrets/jupyterhub.crt secrets/jupyterhub.key userlist

pull:
	docker pull $(DOCKER_NOTEBOOK_IMAGE)

notebook_image: pull

build: check-files network volumes
	docker-compose build

up:
	docker-compose up -d

.PHONY: network volumes check-files pull notebook_image build up
