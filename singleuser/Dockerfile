ARG DOCKER_NOTEBOOK_IMAGE
FROM $DOCKER_NOTEBOOK_IMAGE

ARG JUPYTERHUB_VERSION
RUN python3 -m pip install --no-cache jupyterhub==$JUPYTERHUB_VERSION
RUN /opt/conda/bin/conda install -c conda-forge nbgrader
USER root

COPY ./bin/start-custom.sh /usr/local/bin
COPY ./bin/start-singleuser-custom.sh /usr/local/bin
COPY ./nbgrader_config.py /etc/jupyter
COPY ./students.csv /tmp
# This line is necessary because in the start script we delete user jovyan and without this line wordir is /home/jovyan
WORKDIR /root
