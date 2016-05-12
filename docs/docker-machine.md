## Create a Docker Machine

You can use [Docker Machine](https://docs.docker.com/machine/) to provision a new host, or to connect to an existing host.  In either case, the result will be a "machine" configured on your local workstation or laptop that represents the remote host.  After you activate the machine on your local workstation, when you run `docker` commands locally, Docker Machine will execute them on the remote host for you.

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
