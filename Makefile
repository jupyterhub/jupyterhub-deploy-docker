# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

include .env

.DEFAULT_GOAL=build

network:
	@docker network inspect $(DOCKER_NETWORK_NAME) >/dev/null 2>&1 || docker network create $(DOCKER_NETWORK_NAME)

volumes:
	if [[ $(DATA_VOLUME_HOST) != /* ]]; then\
		@docker volume inspect $(DATA_VOLUME_HOST) >/dev/null 2>&1 \
		|| docker volume create --name $(DATA_VOLUME_HOST)
	fi
	if [[ $(DB_VOLUME_HOST) != /* ]]; then\
		@docker volume inspect $(DB_VOLUME_HOST) >/dev/null 2>&1 \
		|| docker volume create --name $(DB_VOLUME_HOST)
	fi

self-signed-cert:
	# make a self-signed cert

secrets/postgres.env:
	@echo "Generating postgres password in $@"
	@echo "POSTGRES_PASSWORD=$(shell openssl rand -hex 32)" > $@

secrets/oauth.env:
	@echo "## Put Gitlab attributes, for instance" > $@
	@echo "# GITLAB_HOST='https://gitlab.com'" >> $@
	@echo "# OAUTH_CALLBACK_URL='http://localhost:8888/hub/oauth_callback'" >> $@
	@echo "# OAUTH_CLIENT_ID='your-app-id-here'" >> $@
	@echo "# OAUTH_CLIENT_SECRET='your-app-secret-here'" >> $@

secrets/jupyterhub.crt:
	@echo "If you need/have an SSL certificate, name it $@"
	# @exit 1

secrets/jupyterhub.key:
	@echo "If you need/have an SSL key, name it $@"
	# @exit 1

config/userlist:
	@echo "Add usernames, one per line, to $@ if you want to limit the users or define admins"
	@echo " For example:"
	@echo "    zoe admin"
	@echo "    wash"

# Do not require cert/key files if SECRETS_VOLUME defined
secrets_volume = $(shell echo $(SECRETS_VOLUME))
ifeq ($(secrets_volume),)
	cert_files=secrets/jupyterhub.crt secrets/jupyterhub.key
else
	cert_files=
endif

check-files: config/userlist $(cert_files) secrets/oauth.env secrets/postgres.env

pull:
	# docker pull $(BASE_NOTEBOOK_IMAGE)

base_image: singleuser/Dockerfile pull
	docker build -t $(LOCAL_NOTEBOOK_IMAGE) \
		--build-arg JUPYTERHUB_VERSION=$(JUPYTERHUB_VERSION) \
		--build-arg DOCKER_NOTEBOOK_IMAGE=$(BASE_NOTEBOOK_IMAGE) \
		singleuser

isis_image: singleuser/isis.dockerfile pull
	docker build -t $(LOCAL_NOTEBOOK_IMAGE) \
		--build-arg JUPYTERHUB_VERSION=$(JUPYTERHUB_VERSION) \
		--build-arg DOCKER_NOTEBOOK_IMAGE=$(BASE_NOTEBOOK_IMAGE) \
		-f singleuser/isis.dockerfile \
		singleuser

gispy_image: singleuser/gispy.dockerfile pull
	docker build -t $(LOCAL_NOTEBOOK_IMAGE) \
		--build-arg JUPYTERHUB_VERSION=$(JUPYTERHUB_VERSION) \
		--build-arg DOCKER_NOTEBOOK_IMAGE=$(BASE_NOTEBOOK_IMAGE) \
		-f singleuser/gispy.dockerfile \
		singleuser

build: check-files network volumes
	docker-compose build

.PHONY: network volumes check-files pull build base_image isis_image gispy_image
