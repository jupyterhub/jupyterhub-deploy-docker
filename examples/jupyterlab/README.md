# JupyterLab Example

This is an example of using JupyterLab as the single-user Notebook server image with JupyterHub.  The example builds a Docker image that installs the `jupyterlab` notebook server extension.

## Build the Image

Build and tag the image using the `Dockerfile` in this directory.

```
docker build -t jupyterlab .
```

## Run JupyterHub Container

To have JupyterHub spawn the `jupyterlab` image for single-user Notebook
servers, set the following environment variables before you run the JupyterHub container.

```
export DOCKER_NOTEBOOK_IMAGE=jupyterlab
export DOCKER_SPAWN_CMD="start-singleuser.sh --SingleUserNotebookApp.default_url=/lab"
```

Then run the following **from the root directory** of this repository:

```
# bring down the JupyterHub container, if running
docker-compose down

# bring it back up
docker-compose up -d
```
