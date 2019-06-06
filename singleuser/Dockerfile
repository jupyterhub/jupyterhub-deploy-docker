ARG DOCKER_NOTEBOOK_IMAGE
ARG DISPLAY
FROM $DOCKER_NOTEBOOK_IMAGE
ARG JUPYTERHUB_VERSION
#any additional installations go here.
RUN export DISPLAY=$DISPLAY

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    vim \
    htop \
    fonts-dejavu \
    tzdata \
    gfortran \
    gcc

# finish off with MPI dependencies (only required if not installing fenics)
#RUN sudo apt-get install mpich libmpich-dev -y
RUN rm -rf /var/lib/apt/lists/*

USER jovyan
RUN conda update --all
RUN conda install fenics

# If you do not need parallelism, delete the following. 
RUN python3 -m pip install ipyparallel mpi4py
RUN ipython profile create --parallel --profile=mpi
RUN ipython profile create --parallel --profile=default
RUN echo "c.IPClusterEngines.engine_launcher_class = 'MPIEngineSetLauncher'" >> /home/jovyan/.ipython/profile_mpi/ipcluster_config.py

# Python 2 environment
RUN conda create --quiet --yes -p $CONDA_DIR/envs/python2 python=2.7 ipython ipykernel kernda numpy pandas matplotlib ipywidgets yaml ipyparallel mpi4py scipy pyDOE
RUN /opt/conda/envs/python2/bin/ipython profile create --parallel --profile=mpi

USER root
# Create a global kernelspec in the image and modify it so that it properly activates
# the python2 conda environment.
RUN $CONDA_DIR/envs/python2/bin/python -m ipykernel install && \
$CONDA_DIR/envs/python2/bin/kernda -o -y /usr/local/share/jupyter/kernels/python2/kernel.json

USER $NB_UID
# Jupyterhub and memory monitoring
RUN python3 -m pip install --no-cache jupyterhub==$JUPYTERHUB_VERSION nbresuse && \
    jupyter labextension install jupyterlab-topbar-extension && \
    jupyter labextension install jupyterlab-system-monitor && \
    npm cache clean --force && \
    rm -rf $CONDA_DIR/share/jupyter/lab/staging && \
    rm -rf /home/$NB_USER/.cache/yarn && \
    rm -rf /home/$NB_USER/.node-gyp && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER


# Sage
#ENV PATH /opt/conda/envs/python2/bin:$PATH
#ENV CONDA_DEFAULT_ENV /opt/conda/envs/python2 
#ENV CONDA_PREFIX /opt/conda/envs/python2 
RUN python3 -m pip install matplotlib==2.2 
RUN conda install python=3.6.8
RUN conda install --yes -c conda-forge sage 

RUN jupyter labextension install @jupyterlab/git && \
    pip install jupyterlab-git && \
    jupyter serverextension enable --py jupyterlab_git --sys-prefix

# USER SETTINGS
USER jovyan
RUN echo "export EDITOR=/usr/bin/vim" >> /home/jovyan/.bashrc
