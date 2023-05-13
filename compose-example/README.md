# Docker Compose

An example `docker-compose` file and related configuration files are provided
here.

There are four files included in this directory, which can be used as a
starting point, and should be configured to suit your individual needs:-

  - [`Dockerfile`](#Dockerfile)
  - [`docker-compose.yaml`](#docker-compose.yaml)
  - [`jupyterhub_config.py`](#jupyterhub_config.py)
  - [`traefik.yaml`](#traefik.yaml)

# Usage

Configure the files appropriately, and launch the `traefik` and `jupyterhub`
services with the command:-

```
docker-compose up -d
```

# Requirements

- `docker`
- [`docker-compose`](https://docs.docker.com/compose/).
- Optionally, a domain name for LetsEncrypt certificates

## `Dockerfile`

Defines the docker build rules for the `jupyterhub` container image. See
https://jupyterhub-dockerspawner.readthedocs.io/en/latest/docker-image.html for
details on what must be included in this image. This example builds a slimmed
down version of jupyterhub, installing `jupyterhub_traefik_proxy` from
github (not PyPi), along with `dockerspawner` and `oauthenticator` jupyterhub
modules.

## `docker-compose.yaml`

Defines the `jupyterhub_traefik_proxy` and `traefik` service containers that
will be built and run.

Also includes rules for how the traefik API will be accessed. Change the
credentials allowed by the `basicauth` middleware, as it is configured by
default with credentials of `admin` and `password`.

## `jupyterhub_config.py`

jupyterhub's configuration file. Spend some time working through this file.
This is a minimal, but documented example that works for me. A full jupyterhub
configuration can be obtained by running `jupyterhub --generate-config` in the
jupyterhub container. i.e.

```
# Launch the docker-compose project
docker-compose up -d

# Generate a full configuration file, save to jupyterhub_config-full.py
docker-compose exec hub jupyterhub --generate-config > jupyterhub_config-full.py
```

However, a newly generated configuration file won't include configuration
directives for everything you might want to use, e.g.
`jupyterhub_traefik_proxy`,
[`oauthenticator`](https://github.com/jupyterhub/oauthenticator), or
[`dockerspawner`](https://jupyterhub-dockerspawner.readthedocs.io/). The
relevant documentation (or code) for non-default modules should be referred to.

## `traefik.yaml`

The static configuration file used by `traefik`. This file can be used to
configure various features on traefik, including but not limited to:-

- [ACME certificate resolvers](https://doc.traefik.io/traefik/https/acme/)
- [traefik entrypoints](https://doc.traefik.io/traefik/routing/entrypoints/)
- [traefik log](https://doc.traefik.io/traefik/observability/logs/)
- [traefik API](https://doc.traefik.io/traefik/operations/api/)

