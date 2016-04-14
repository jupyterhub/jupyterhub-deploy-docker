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
* This example configures JupyterHub for HTTPS connections (the default).  As such, you must provide TLS certificate chain and key files to the JupyterHub server.  If you do not have your own certificate chain and key, you can either create self-signed versions, or obtain real ones from [Let's Encrypt](https://letsencrypt.org) (see the [letsencrypt example](examples/letsencrypt/README.md) for instructions).

## Create a Docker Machine

Use [Docker Machine](https://docs.docker.com/machine/) to provision a new host, or to connect to an existing one.   

This example assumes that a remote host already exists at IP address `10.0.0.10`, and that you can perform password-less login to this host from your local workstation or laptop using a private SSH key.

To create a Docker machine that will install and configure the Docker daemon on an existing host (note that Docker Machine will upgrade the Docker daemon on the host if it is already installed):

```
# Use the generic driver to create a Docker machine that
# controls the Docker daemon on an existing host
export DRIVER_OPTS="--driver generic \
  --generic-ip-address 10.0.0.10 \
  --generic-ssh-key /path/to/private/ssh/key"

# Create a machine named jupyterhub
docker-machine create $DRIVER_OPTS jupyterhub

# Activate the machine
eval "$(docker-machine env jupyterhub)"
```

Docker Machine can also provision new hosts using one of it's [supported drivers](https://docs.docker.com/machine/drivers/).   When provisioning a host, Docker Machine will automatically generate TLS certificate and key files and use them to authenticate with the remote Docker daemon.

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

## Run the JupyterHub container

Run the JupyterHub container on the host.  

To run the JupyterHub container in detached mode:

```
./hub.sh up -d
```

Once the container is running, you should be able to navigate to the JupyterHub console at

```
https://myhost.mydomain
```

To bring down the JupyterHub container:

```
./hub.sh down
```
