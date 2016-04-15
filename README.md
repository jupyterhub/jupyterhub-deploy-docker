# jupyterhub-deploy-docker

This repository provides a reference deployment of [JupyterHub](https://github.com/jupyter/jupyterhub), a multi-user [Jupyter Notebook](http://jupyter.org/) environment, on a **single host** using [Docker](https://docs.docker.com).  

This deployment:

* Runs the [JupyterHub components](https://jupyterhub.readthedocs.org/en/latest/getting-started.html#overview) in a Docker container on the host
* Uses [DockerSpawner](https://github.com/jupyter/dockerspawner) to spawn single-user Jupyter Notebook servers in separate Docker containers on the same host
* Persists JupyterHub data in a Docker volume on the host
* Persists user notebook directories in Docker volumes on the host
* Uses [OAuthenticator](https://github.com/jupyter/oauthenticator) and [GitHub OAuth](https://developer.github.com/v3/oauth/) to authenticate users

![JupyterHub single host Docker deployment](internal/jupyterhub-docker.png)

## Use Cases

Possible use cases for this deployment may include, but are not limited to:

* A JupyterHub demo environment that you can spin up relatively quickly.
* A multi-user Jupyter Notebook environment for small classes, teams, or departments.

## Disclaimer

This deployment is **NOT** intended for a production environment.  

## Prerequisites

* This deployment uses Docker for all the things. It assumes that you wiil be using [Docker Machine](https://docs.docker.com/machine/overview/) and [Docker Compose](https://docs.docker.com/compose/overview/) on a local workstation or laptop to create, build, and run Docker images on a remote host.  It requires [Docker Toolbox](https://www.docker.com/products/docker-toolbox) 1.11.0 or higher.  See the [installation instructions](https://docs.docker.com/engine/installation/) for your environment.
* This example configures JupyterHub for HTTPS connections (the default).  As such, you must provide TLS certificate chain and key files to the JupyterHub server.  If you do not have your own certificate chain and key, you can either [create self-signed versions](https://jupyter-notebook.readthedocs.org/en/latest/public_server.html#using-ssl-for-encrypted-communication), or obtain real ones from [Let's Encrypt](https://letsencrypt.org) (see the [letsencrypt example](examples/letsencrypt/README.md) for instructions).

## Create a Docker Machine

Use [Docker Machine](https://docs.docker.com/machine/) to provision a new host, or to connect to an existing host.  In either case, the result will be a "machine" configured on your local workstation or laptop that represents the remote host.  After you activate the machine on your local workstation, when you run `docker` commands locally, Docker Machine will execute them on the remote host for you.

### Provision a new host

Docker Machine can provision new hosts on various platforms using one of its [supported drivers](https://docs.docker.com/machine/drivers/).   When provisioning a host, Docker Machine will automatically install the latest version of [Docker Engine](https://www.docker.com/products/docker-engine) on the host.  It will also generate local TLS certificate and key files to connect to the host and authenticate with the `docker` daemon on the host.

In the following example, we provision a new virtual server on [IBM SoftLayer](https://www.softlayer.com/promo/freeCloud/freecloud).  (You can provision similarly on RackSpace, AWS, and other hosting providers).  We set `DRIVER_OPTS` to the SoftLayer-specific options.

```
# Set Docker Machine SoftLayer driver options
export DRIVER_OPTS="--driver softlayer \
  --softlayer-api-key <my_softlayer_api_key> \
  --softlayer-user <my_softlayer_username> \
  --softlayer-domain mydomain \
  --softlayer-cpu 16 \
  --softlayer-memory 65536 \
  --softlayer-disk-size 100 \
  --softlayer-region wdc01"
  
# Create a machine named jupyterhub
docker-machine create $DRIVER_OPTS jupyterhub

```

### Connect to an existing host

This example configures a "machine" on your local workstation that connects to an existing remote host at IP address `10.0.0.10`.  To do this, you must use Docker Machine's `generic` driver, and your local workstation must have a private SSH key that allows you to perform password-less login to the host.

Substitute your own IP address and path to SSH key in the `DRIVER_OPTS` below.  Note that when you run the `docker-machine create` command, Docker Machine will install and configure the latest Docker Engine on the remote host (or upgrade the Docker Engine on the host if it is already installed).

```
# Use the generic driver to create a Docker machine that
# controls the Docker daemon on an existing host
export DRIVER_OPTS="--driver generic \
  --generic-ip-address 10.0.0.10 \
  --generic-ssh-key /Users/jtyberg/.ssh/myhost_rsa.pem"

# Create a machine named jupyterhub
docker-machine create $DRIVER_OPTS jupyterhub
```

## Activate Docker Machine

You must set specific `DOCKER_*` environment variables to tell `docker` that it should run commands against a particular machine.  The remainder of this document assumes that the machine called `jupyterhub` is active, and therefore, all `docker` commands will run on the `jupyterhub` remote host.

To set the `jupyterhub` machine as active:

```
eval "$(docker-machine env jupyterhub)"
```

All this does is set the right environment variables:

```
env|grep DOCKER

DOCKER_HOST=tcp://10.0.0.10:2376
DOCKER_MACHINE_NAME=jupyterhub
DOCKER_TLS_VERIFY=1
DOCKER_CERT_PATH=/Users/jtyberg/.docker/machine/machines/jupyterhub
```


To see which machine is active:

```
docker-machine active
```

## Create a Docker Network

Create a Docker network for inter-container communication.  The benefits of using a Docker network are:

* container isolation - only the containers on the network can access one another
* name resolution - Docker daemon runs an embedded DNS server to provide automatic service discovery for containers connected to user-defined networks.  This allows us to access containers on the same network by name.

Here we create a Docker network named `jupyterhub-network`.  Later, we will configure the JupyterHub and single-user Jupyter Notebook containers to run attached to this network.

```
docker network create jupyterhub-network
```

## Setup GitHub Authentication

This deployment uses GitHub OAuth to authenticate users.  It requires that you create a [GitHub application](https://github.com/settings/applications/new). You will need to specify an OAuth callback URL in the following form:

```
https://<myhost.mydomain>/hub/oauth_callback
```

You must pass the secrets that GitHub provides for your application to JupyterHub at runtime.  You can do this by setting the `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, and `OAUTH_CALLBACK_URL` environment variables when you run the JupyterHub container, or you can add them to the `.env` file in the root directory of this repository.  For example,

```
GITHUB_CLIENT_ID=<github_client_id>
GITHUB_CLIENT_SECRET=<github_client_secret>
OAUTH_CALLBACK_URL=https://<myhost.mydomain>/hub/oauth_callback
```

**Note:** The `.env` file is a special file that Docker Compose uses to lookup environment variables.  If you choose to place the GitHub secrets in this file, you should ensure that this file remains private (e.g., do not commit the secrets to source control).

## Build the JupyterHub Docker image

Configure JupyterHub and build it into a Docker image.

1. Copy your TLS certificate and key to a directory named `secrets` within this repository directory.  These will be added to the Docker image at build time.

    ```
    mkdir -p secrets
    cp jupyterhub.cer jupyterhub.key secrets/
    ```

1. Create a `userlist` file with a list of authorized users.  At a minimum, this file should contain a single admin user.  The username should be a GitHub username.  For example:

  	```
  	jtyberg admin
  	```

	The admin user will have the ability to add more users in the JupyterHub admin console.

1. Build the JupyterHub Docker image.  For convenience, this repo provides a `hub.sh` script that wraps [docker-compose](https://docs.docker.com/compose/reference/), so you can run it with the docker-compose [command line arguments](https://docs.docker.com/compose/reference/overview/).  To build the JupyterHub image on the active Docker machine host, run:

    ```
    ./hub.sh build
    ```

## Create a JupyterHub Data Volume

Create a Docker volume to persist JupyterHub data.   This volume will reside on the host machine.  Using a volume allows user lists, cookies, etc., to persist across JupyterHub container restarts.

```
docker volume create --name jupyterhub-data
```

## Pull the Jupyter Notebook Image

Pull the Jupyter Notebook Docker image that you would like JupyterHub to spawn for each user.  

Note: Even though Docker will pull the image to the host the first time a user container is spawned, JupyterHub may timeout if the image is large, so it's better to do it beforehand.

This deployment uses the [jupyter/scipy-notebook](https://hub.docker.com/r/jupyter/scipy-notebook/) Docker image, which is built from the `scipy-notebook` [Docker stacks](https://github.com/jupyter/docker-stacks).  

Note that the Docker stacks `*-notebook` images tagged `2d878db5cbff` include the `start-singleuser.sh` script required to start a single-user instance of the Notebook server that is compatible with JupyterHub.

```
docker pull jupyter/scipy-notebook:2d878db5cbff
```

Note: If you choose to use a different container image, be sure to set the `DOCKER_CONTAINER_IMAGE` environment variable either in the shell you use to launch JupyterHub or in the `.env` file.

## Run the JupyterHub container

Run the JupyterHub container on the host.  

To run the JupyterHub container in detached mode:

```
./hub.sh up -d
```

Once the container is running, you should be able to access the JupyterHub console at

```
https://myhost.mydomain
```

To bring down the JupyterHub container:

```
./hub.sh down
```

## FAQ

### How can I view the logs for JupyterHub or users' Notebook servers?

Use `docker logs <container>`.  For example, to view the logs of the `jupyterhub` container

```
docker logs jupyterhub
```

### How can I backup a user's notebook directory?

There are multiple ways to [backup and restore](https://docs.docker.com/engine/userguide/containers/dockervolumes/#backup-restore-or-migrate-data-volumes) data in Docker containers.  

Suppose you have the following running containers:

```
docker ps --format "table {{.ID}}\t{{.Image}}\t{{.Names}}"

CONTAINER ID        IMAGE                    NAMES
bc02dd6bb91b        jupyter/minimal-notebook jupyter-jtyberg
7b48a0b33389        jupyterhub               jupyterhub
```

In this deployment, the user's notebook directories (`/home/jovyan/work`) are backed by Docker volumes.

```
docker inspect -f '{{ .Mounts }}' jupyter-jtyberg

[{jtyberg /var/lib/docker/volumes/jtyberg/_data /home/jovyan/work local rw true rprivate}]
```

We can backup the user's notebook directory by running a separate container that mounts the user's volume and creates a tarball of the directory.  

```
docker run --rm \
  -u root \
  -v /tmp:/backups \
  -v jtyberg:/notebooks \
  jupyter/minimal-notebook \
  tar cvf /backups/jtyberg-backup.tar /notebooks
```

The above command creates a tarball in the `/tmp` directory on the host.