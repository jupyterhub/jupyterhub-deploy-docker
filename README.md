# docker-jupyterhub-deploy

Provides a reference
deployment of [JupyterHub](https://github.com/jupyter/jupyterhub), a
multi-user [Jupyter Notebook](http://jupyter.org/) environment, on a
**single host** using [Docker](https://docs.docker.com).

Possible **use cases** include:

* Providing a multi-user Jupyter Notebook environment for small classes,
  teams, or departments.
* Creating a JupyterHub demo environment that you can spin up relatively
  quickly.

[jupyterhub/jupyterhub-deploy-docker]: https://github.com/jupyterhub/jupyterhub-deploy-docker

This repository is an customization of [jupyterhub/jupyterhub-deploy-docker][],
adapted for our team of **planetary** researchers and data scientists.

> **Notice:** this repository is about Jupyter-<i>Hub</i>, the component responsible
> for managing multiple Jupyter-<i>Lab</i> servers, in a multi-user environment.
> If you are looking for the Jupyter-Lab images ready for your personal use for
> planetary/remote-sensing data analysis, have a look at:
> [docker-isis](https://github.com/europlanet-gmap/docker-isis).


## Technical Overview

Key components of this reference deployment are:

* **Host**: Runs the [JupyterHub components](https://jupyterhub.readthedocs.org/en/latest/getting-started.html#overview)
  in a Docker container on the host.

* **Authenticator**: Optionally uses [OAuthenticator](https://github.com/jupyter/oauthenticator).

* **Spawner**:Uses [DockerSpawner](https://github.com/jupyter/dockerspawner)
  to spawn single-user Jupyter Notebook servers in separate Docker
  containers on the same host.

* **Persistence of Hub data**: Persists JupyterHub data in a Docker
  volume on the host.

* **Persistence of user notebook directories**: Persists user notebook
  directories in Docker volumes on the host.

<img src="assets/jupyterhub-docker.png" width="500"/>


## Set up & Run it

The basic steps to run the JupyterHub using the default settings are provided below.

> This deployment uses Docker, via [Docker Compose](https://docs.docker.com/compose/overview/).
  [Docker Engine](https://docs.docker.com/engine) 1.12.0 or higher is required.

Before we run and start using Jupyter, we must setup the environment:

1. build jupyterhub image
2. build notebook image

Then, we are ready to run it.

The following commands should get you going with a default setup:

Build the images:
```bash
docker-compose -f images-build.yml build
```

Run the Hub:
```bash
docker-compose up
```

This will start a Jupyter-Hub at `http://localhost:8000`,
with a dummy ("everybody-aloud") user authentication,
and system and user files under `./tmp/` folder.


## Settings

For details about features and settings, refer to [docs/](docs/):

- [docs/settings.md](docs/settings.md)
- [docs/deployment.md](docs/deployment.md)


## Contributing

If you have suggestions or are having difficultis, please let us know in the
*issues*. Pull requests to code or documentation are all very welcome:

- [CONTRIBUTING.md](CONTRIBUTING.md)


/.\
