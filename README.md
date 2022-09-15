**[Technical Overview](#technical-overview)** |
**[Prerequisites](#prerequisites)** |
**[Authenticator setup](#authenticator-setup)** |
**[Build the JupyterHub Docker image](#build-the-jupyterhub-docker-image)** |
**[Spawner: Prepare the Jupyter Notebook Image](#spawner-prepare-the-jupyter-notebook-image)** |
**[Run JupyterHub](#run-jupyterhub)** |
**[Behind the scenes](#behind-the-scenes)** |
**[FAQ](#faq)**

# jupyterhub-deploy-docker

**jupyterhub-deploy-docker** provides a reference
deployment of [JupyterHub](https://github.com/jupyter/jupyterhub), a
multi-user [Jupyter Notebook](http://jupyter.org/) environment, on a
**single host** using [Docker](https://docs.docker.com).

Possible **use cases** include:

- Creating a JupyterHub demo environment that you can spin up relatively
  quickly.
- Providing a multi-user Jupyter Notebook environment for small classes,
  teams, or departments.

## Disclaimer

This deployment is **NOT** intended for a production environment.
It is a reference implementation that does not meet traditional
requirements in terms of availability nor scalability.

If you are looking for a more robust solution to host JupyterHub, or
you require scaling beyond a single host, please check out the
excellent [zero-to-jupyterhub-k8s](https://github.com/jupyterhub/zero-to-jupyterhub-k8s)
project.

## Technical Overview

Key components of this reference deployment are:

- **Host**: Runs the [JupyterHub components](https://jupyterhub.readthedocs.org/en/latest/getting-started.html#overview)
  in a Docker container on the host.

- **Authenticator**: Uses [Native Authenticator](https://github.com/jupyterhub/nativeauthenticator) to authenticate users.

- **Spawner**:Uses [DockerSpawner](https://github.com/jupyter/dockerspawner)
  to spawn single-user Jupyter Notebook servers in separate Docker
  containers on the same host.

- **Persistence of Hub data**: Persists JupyterHub data in a Docker
  volume on the host.

- **Persistence of user notebook directories**: Persists user notebook
  directories in Docker volumes on the host.

## Prerequisites

### Docker

This deployment uses Docker, via [Docker Compose](https://docs.docker.com/compose/), for all the things.

1. Use [Docker's installation instructions](https://docs.docker.com/engine/installation/)
   to set up Docker for your environment.

## Authenticator setup

This deployment uses [JupyterHub Native Authenticator](https://native-authenticator.readthedocs.io/en/latest/) to authenticate users.

1. An single `admin` user will be enabled be default.

## Build the JupyterHub Docker image

1. Use [docker-compose](https://docs.docker.com/compose/reference/) to build
   the JupyterHub Docker image on the active Docker machine host by running
   the `make build` command:

   ```bash
   docker-compose build
   ```

## Customisation: Jupyter Notebook Image

You can configure JupyterHub to spawn Notebook servers from any Docker image, as
long as the image's `ENTRYPOINT` and/or `CMD` starts a single-user instance of
Jupyter Notebook server that is compatible with JupyterHub.

To specify which Notebook image to spawn for users, you set the value of the  
`DOCKER_NOTEBOOK_IMAGE` environment variable to the desired container image.

Whether you build a custom Notebook image or pull an image from a public or
private Docker registry, the image must reside on the host.

If the Notebook image does not exist on host, Docker will attempt to pull the
image the first time a user attempts to start his or her server. In such cases,
JupyterHub may timeout if the image being pulled is large, so it is better to
pull the image to the host before running JupyterHub.

This deployment defaults to the
[jupyter/minimal-notebook](https://hub.docker.com/r/jupyter/minimal-notebook/)
Notebook image, which is built from the `minimal-notebook`
[Docker stacks](https://github.com/jupyter/docker-stacks).

You can pull the image using the following command:

```bash
docker pull jupyter/minimal-notebook
```

## Run JupyterHub

Run the JupyterHub container on the host.

To run the JupyterHub container in detached mode:

```bash
docker-compose up -d
```

Once the container is running, you should be able to access the JupyterHub console at

```
http://localhost:8000
```

To bring down the JupyterHub container:

```bash
docker-compose down
```

---

## FAQ

### How can I view the logs for JupyterHub or users' Notebook servers?

Use `docker logs <container>`. For example, to view the logs of the `jupyterhub` container

```bash
docker logs jupyterhub
```

### How do I specify the Notebook server image to spawn for users?

In this deployment, JupyterHub uses DockerSpawner to spawn single-user
Notebook servers. You set the desired Notebook server image in a
`DOCKER_NOTEBOOK_IMAGE` environment variable.

JupyterHub reads the Notebook image name from `jupyterhub_config.py`, which
reads the Notebook image name from the `DOCKER_NOTEBOOK_IMAGE` environment
variable:

```python
# DockerSpawner setting in jupyterhub_config.py
c.DockerSpawner.image = os.environ['DOCKER_NOTEBOOK_IMAGE']
```

### If I change the name of the Notebook server image to spawn, do I need to restart JupyterHub?

Yes. JupyterHub reads its configuration which includes the container image
name for DockerSpawner. JupyterHub uses this configuration to determine the
Notebook server image to spawn during startup.

If you change DockerSpawner's name of the Docker image to spawn, you will
need to restart the JupyterHub container for changes to occur.

In this reference deployment, cookies are persisted to a Docker volume on the
Hub's host. Restarting JupyterHub might cause a temporary blip in user
service as the JupyterHub container restarts. Users will not have to login
again to their individual notebook servers. However, users may need to
refresh their browser to re-establish connections to the running Notebook
kernels.

### How can I backup a user's notebook directory?

There are multiple ways to [backup and restore](https://docs.docker.com/engine/userguide/containers/dockervolumes/#backup-restore-or-migrate-data-volumes) data in Docker containers.

Suppose you have the following running containers:

```bash
    docker ps --format "table {{.ID}}\t{{.Image}}\t{{.Names}}"

    CONTAINER ID        IMAGE                    NAMES
    bc02dd6bb91b        jupyter/minimal-notebook jupyter-jtyberg
    7b48a0b33389        jupyterhub               jupyterhub
```

In this deployment, the user's notebook directories (`/home/jovyan/work`) are backed by Docker volumes.

```bash
    docker inspect -f '{{ .Mounts }}' jupyter-jtyberg

    [{jtyberg /var/lib/docker/volumes/jtyberg/_data /home/jovyan/work local rw true rprivate}]
```

We can backup the user's notebook directory by running a separate container that mounts the user's volume and creates a tarball of the directory.

```bash
docker run --rm \
  -u root \
  -v /tmp:/backups \
  -v jtyberg:/notebooks \
  jupyter/minimal-notebook \
  tar cvf /backups/jtyberg-backup.tar /notebooks
```

The above command creates a tarball in the `/tmp` directory on the host.
