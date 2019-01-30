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
# finish off with MPI dependencies
RUN sudo apt-get install mpich libmpich-dev && \
     rm -rf /var/lib/apt/lists/*

USER jovyan

RUN python3 -m pip install --no-cache jupyterhub==$JUPYTERHUB_VERSION nbresuse 
RUN conda install -c conda-forge fenics

RUN python3 -m pip install ipyparallel mpi4py
RUN ipython profile create --parallel --profile=mpi
RUN echo "c.IPClusterEngines.engine_launcher_class = 'MPIEngineSetLauncher'" >> /home/jovyan/.ipython/profile_mpi/ipcluster_config.py

RUN conda create --quiet --yes -p $CONDA_DIR/envs/python2 python=2.7 ipython ipykernel kernda numpy pandas matplotlib ipywidgets yaml ipyparallel mpi4py 
RUN /opt/conda/envs/python2/bin/ipython profile create --parallel --profile=mpi

USER root

# Create a global kernelspec in the image and modify it so that it properly activates
# the python2 conda environment.
RUN $CONDA_DIR/envs/python2/bin/python -m ipykernel install && \
$CONDA_DIR/envs/python2/bin/kernda -o -y /usr/local/share/jupyter/kernels/python2/kernel.json

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libapparmor1 \
        libedit2 \
        lsb-release \
        psmisc \
        libssl1.0.0 \
        ;

# You can use rsession from rstudio's desktop package as well.
ENV RSTUDIO_PKG=rstudio-server-1.1.463-amd64.deb

RUN wget -q http://download2.rstudio.org/${RSTUDIO_PKG}
RUN dpkg -i ${RSTUDIO_PKG}
RUN rm ${RSTUDIO_PKG}
RUN conda install -c r r-shiny && conda clean -tipsy
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*

USER $NB_USER
# The desktop package uses /usr/lib/rstudio/bin
RUN python3 -m pip install jupyter-rsession-proxy
RUN python3 -m pip install git+https://github.com/jupyterhub/jupyter-rsession-proxy
RUN jupyter labextension install jupyterlab-server-proxy
ENV PATH="${PATH}:/usr/lib/rstudio-server/bin"
ENV LD_LIBRARY_PATH="/usr/lib/R/lib:/lib:/usr/lib/jvm/java-7-openjdk-amd64/jre/lib/amd64/server:/opt/conda/lib/R/lib"
#ENV LD_LIBRARY_PATH="/usr/lib/R/lib:/lib:/usr/lib/x86_64-linux-gnu:/usr/lib/jvm/java-7-openjdk-amd64/jre/lib/amd64/server:/opt/conda/lib/R/lib"

USER jovyan
RUN echo "export EDITOR=/usr/bin/vim" >> /home/jovyan/.bashrc
