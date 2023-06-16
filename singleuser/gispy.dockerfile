ARG BASE_IMAGE="gmap/jupyter-gispy:latest"
FROM $BASE_IMAGE

ARG JUPYTERHUB_VERSION="3.0.0"
RUN python3 -m pip install --no-cache jupyterhub==$JUPYTERHUB_VERSION

COPY etc/jupyterlab/user_settings.json /opt/conda/share/jupyter/lab/settings/overrides.json

COPY bin/start-gmapuser.sh /usr/local/bin/start-gmapuser.sh
