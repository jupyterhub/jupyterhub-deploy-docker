# Custom Jupyter Notebook Server Image

This is an example of using a custom Jupyter Notebook server Docker image with JupyterHub.  The `Dockerfile` builds from the `jupyter/scipy-notebook` image, but customizes the image in the following ways:

* installs an additional Python package to make it available to notebooks
* uses a custom entrypoint script that copies sample notebooks to the user's notebook directory before executing the run command that was provided to the container

## Build the Image

Build and tag the image using the `Dockerfile` in this directory.

```
docker build -t my-custom-notebook .
```

## Run JupyterHub Container

To have JupyterHub spawn the `my-custom-notebook` image for single-user Notebook
servers, set the `DOCKER_NOTEBOOK_IMAGE` environment variable to the image name
when you run the JupyterHub container.  For example, run the following
**from the root directory** of this repository:

```
export DOCKER_NOTEBOOK_IMAGE=my-custom-notebook

# bring down the JupyterHub container, if running
docker-compose down

# bring it back up
docker-compose up -d
```
