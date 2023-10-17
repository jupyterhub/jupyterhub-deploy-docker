ARG BASE_IMAGE="jupyter/minimal-notebook:latest"
FROM $BASE_IMAGE

ARG JUPYTERHUB_VERSION="4"

# Guarantee pip is up-to-date
RUN python3 -m pip install --no-cache --upgrade \
      setuptools \
      pip

RUN python3 -m pip install --no-cache jupyterhub==$JUPYTERHUB_VERSION
