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

RUN source activate isis  && \
    pip install ipykernel &&\
    python -m ipykernel install --user --name 'ISIS'

# # ENV ISISROOT=/opt/conda
# ARG ISISDATA=/isis/data
# ARG ISISTESTDATA=/isis/testdata
#
# USER root
# RUN mkdir -p $ISISDATA && \
#     mkdir -p $ISISTESTDATA
# USER $NB_UID
#
# RUN source activate isis && \
#     python /opt/conda/envs/isis/scripts/isisVarInit.py \
#       --data-dir=$ISISDATA  \
#       --test-dir=$ISISTESTDATA && \
#     echo "source activate isis" >> $HOME/.bashrc

RUN echo 'source activate isis' >> $HOME/.bashrc          && \
    echo 'python ${CONDA_PREFIX}/scripts/isisVarInit.py'  \
          '--data-dir=${ISISDATA_DIR} --quiet'            \
          >> $HOME/.bashrc                                && \
    echo 'conda deactivate' >> $HOME/.bashrc              && \
    echo 'source activate isis' >> $HOME/.bashrc
