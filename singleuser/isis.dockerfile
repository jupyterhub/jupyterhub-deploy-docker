ARG DOCKER_NOTEBOOK_IMAGE
FROM $DOCKER_NOTEBOOK_IMAGE
ARG JUPYTERHUB_VERSION
RUN python3 -m pip install --no-cache jupyterhub==$JUPYTERHUB_VERSION

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

USER root
RUN apt-get update && \
    # apt-get install -y --no-install-recommends s3cmd && \
    apt-get install -y libgl1-mesa-glx && \
    apt-get install -y libjpeg9 libjpeg9-dev && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get autoremove
USER $NB_UID

RUN conda create -n isis -c conda-forge -y python=3.6     && \
    source activate isis                                  && \
    conda config --add channels conda-forge               && \
    conda config --prepend channels usgs-astrogeology     && \
    conda config --append channels default                && \
    mamba install -c usgs-astrogeology -y isis            && \
    conda clean -a

RUN source activate isis                                    && \
    pip install ipykernel                                   && \
    python -m ipykernel install --user --name 'ISIS'

# ENV BASH_PROFILE=/etc/profile.d/isis.sh
ENV ISIS_PROFILE=/home/jovyan/.bashrc

RUN source activate isis                                    && \
    echo "ISISROOT=$CONDA_PREFIX" \
        >> $ISIS_PROFILE          && \
    echo 'ISISDATA=${ISISDATA_DIR:?"Missing IsisData-Dir. This is wrong."}' \
        >> $ISIS_PROFILE  && \
    echo 'ISISTESTDATA=${HOME}/.isis/testdata' \
        >> $ISIS_PROFILE   && \
    echo 'ALESPICEROOT=${HOME}/.isis/aledata' \
        >> $ISIS_PROFILE    && \
    echo 'mkdir -p $ISISTESTDATA $ALESPICEROOT' \
        >> $ISIS_PROFILE  && \
    echo 'export ISISROOT ISISDATA ISISTESTDATA ALESPICEROOT'     \
        >> $ISIS_PROFILE  && \
    echo 'source activate isis' >> $ISIS_PROFILE

# RUN echo 'source activate isis' >> $HOME/.bashrc          && \
#     echo 'python ${CONDA_PREFIX}/scripts/isisVarInit.py'  \
#           '--data-dir=${ISISDATA_DIR} --quiet'            \
#           >> $HOME/.bashrc                                && \
#     echo 'conda deactivate' >> $HOME/.bashrc              && \
#     echo 'source activate isis' >> $HOME/.bashrc

RUN echo 'export PATH="${HOME}/.local/bin:${PATH}"' >> $HOME/.bashrc

# If WORK_DIR is not defined (when notebook/user is started), use (~) Home.
RUN echo 'conda config --add envs_dirs ${WORK_DIR:-~}/.conda/envs 2> /dev/null' \
      >> $HOME/.bashrc

# RUN python3 -m pip install nbgitpuller
# RUN echo 'http://localhost:8888/hub/user-redirect/git-pull?repo=https%3A%2F%2Fgithub.com%2Feuroplanet-gmap%2FBasemappingUtils&urlpath=lab%2Ftree%2FBasemappingUtils%2FREADME.md&branch=master' > $HOME/README.md

COPY etc/jupyterlab/user_settings.json /opt/conda/share/jupyter/lab/settings/overrides.json

COPY bin/start-gmapuser.sh /usr/local/bin/start-gmapuser.sh
