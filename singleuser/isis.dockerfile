ARG BASE_IMAGE="jupyter/minimal-notebook:latest"
FROM $BASE_IMAGE

ARG JUPYTERHUB_VERSION="3.0.0"
RUN python3 -m pip install --no-cache jupyterhub==$JUPYTERHUB_VERSION

# # If WORK_DIR is not defined (when notebook/user is started), use (~) Home.
# RUN echo 'conda config --add envs_dirs ${WORK_DIR:-~}/.conda/envs 2> /dev/null' \
#       >> $HOME/.bashrc

# RUN python3 -m pip install nbgitpuller
# RUN echo 'http://localhost:8888/hub/user-redirect/git-pull?repo=https%3A%2F%2Fgithub.com%2Feuroplanet-gmap%2FBasemappingUtils&urlpath=lab%2Ftree%2FBasemappingUtils%2FREADME.md&branch=master' > $HOME/README.md

COPY etc/jupyterlab/user_settings.json /opt/conda/share/jupyter/lab/settings/overrides.json

COPY bin/start-gmapuser.sh /usr/local/bin/start-gmapuser.sh
