ARG DOCKER_NOTEBOOK_IMAGE
FROM $DOCKER_NOTEBOOK_IMAGE
ARG JUPYTERHUB_VERSION
#any additional installations go here.

USER root

RUN apt-get update && \
    apt-get install -y vim && \
    apt-get install -y gcc && \
    rm -rf /var/lib/apt/lists/*

USER jovyan

RUN python3 -m pip install --no-cache jupyterhub==$JUPYTERHUB_VERSION nbresuse
RUN conda install -c conda-forge fenics
