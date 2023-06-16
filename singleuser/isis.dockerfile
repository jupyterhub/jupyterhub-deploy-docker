ARG DOCKER_NOTEBOOK_IMAGE="jupyter/minimal-notebook:latest"
FROM $DOCKER_NOTEBOOK_IMAGE

ARG JUPYTERHUB_VERSION="3.0.0"
RUN python3 -m pip install --no-cache jupyterhub==$JUPYTERHUB_VERSION

# This lines above are necessary to guarantee a smooth coupling JupyterHub.
# -------------------------------------------------------------------------

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

USER root
RUN apt-get update                              && \
    apt-get install -y --no-install-recommends  \
        bzip2           						\
        ca-certificates 						\
        curl            						\
        git             						\
        libgl1-mesa-glx 						\
        libjpeg9        						\
        libjpeg9-dev    						\
        rsync           						\
        wget            						\
        vim             					    && \
    rm -rf /var/lib/apt/lists/*                 && \
    apt-get autoremove
USER $NB_UID

ARG ISIS_VERSION="7.1.0"
ARG ASP_VERSION="3.2.0"

RUN conda create -n isis -c conda-forge -y python=3.9

RUN source activate isis                                            && \
    conda config --add channels conda-forge                         && \
    conda config --env --prepend channels usgs-astrogeology         && \
    conda config --env --prepend channels nasa-ames-stereo-pipeline && \
    conda config --append channels default                          && \
    mamba install stereo-pipeline=${ASP_VERSION}                    && \
    mamba install -c usgs-astrogeology -y isis=${ISIS_VERSION}      && \
    conda clean -a

RUN source activate isis                                    && \
    pip install ipykernel                                   && \
    python -m ipykernel install --user --name 'ISIS-ASP'

ARG ISISDATA="/isis/data"
ARG ISISTESTDATA="/isis/testdata"

ENV ISISDATA=${ISISDATA}
ENV ISISTESTDATA=${ISISTESTDATA}

ENV ISISROOT="/opt/conda/envs/isis"

RUN echo 'source activate isis' >> ~/.bashrc                        && \
    echo 'export PATH="${HOME}/.local/bin:${PATH}"' >> ~/.bashrc

RUN DOC="${HOME}/README.md" && \
    echo "# Planeraty data science environment" > $DOC  && \
    echo "" >> $DOC && \
    echo "- ISIS version: ${ISIS_VERSION}" >> $DOC && \
    echo "- ASP version: ${ASP_VERSION}" >> $DOC 

# # If WORK_DIR is not defined (when notebook/user is started), use (~) Home.
# RUN echo 'conda config --add envs_dirs ${WORK_DIR:-~}/.conda/envs 2> /dev/null' \
#       >> $HOME/.bashrc

# RUN python3 -m pip install nbgitpuller
# RUN echo 'http://localhost:8888/hub/user-redirect/git-pull?repo=https%3A%2F%2Fgithub.com%2Feuroplanet-gmap%2FBasemappingUtils&urlpath=lab%2Ftree%2FBasemappingUtils%2FREADME.md&branch=master' > $HOME/README.md

# COPY etc/jupyterlab/user_settings.json /opt/conda/share/jupyter/lab/settings/overrides.json

# COPY bin/start-gmapuser.sh /usr/local/bin/start-gmapuser.sh
