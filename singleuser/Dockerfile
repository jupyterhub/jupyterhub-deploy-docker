ARG DOCKER_NOTEBOOK_IMAGE
ARG DISPLAY
FROM $DOCKER_NOTEBOOK_IMAGE
ARG JUPYTERHUB_VERSION
#any additional installations go here.
RUN export DISPLAY=$DISPLAY

USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    texlive \
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-science \
    latexmk \
    tzdata \
    dvipng \
    lmodern \ 
    ghostscript \
    context \
    fonts-lato \
    fonts-dejavu \
    texlive-xetex \
    texlive-luatex \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    vim \
    htop \
    qrencode \
    screen \
    imagemagick \
    gfortran \
    gcc

# build font caches
RUN mtxrun --script fonts --reload && \
    luaotfload-tool --update

# finish off with MPI dependencies (only required if not installing fenics)
#RUN sudo apt-get install mpich libmpich-dev -y
RUN rm -rf /var/lib/apt/lists/*

USER $NB_UID

RUN conda update -n base --yes conda
#RUN conda update --all --yes
RUN conda install --yes fenics

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

# Packages
RUN python3 -m pip install --no-cache \
        astropy
        #jupyterlab_latex && \
        #jupyter labextension install @jupyterlab/latex

RUN conda install --yes -c conda-forge jupyter_contrib_nbextensions ipywidgets
RUN conda install -c plotly plotly plotly-orca psutil

# Jupyterhub and memory monitoring
RUN python3 -m pip install --no-cache jupyterhub==$JUPYTERHUB_VERSION nbresuse

# things to make the lab environment better.
#RUN jupyter labextension install jupyterlab-drawio && \
#    jupyter labextension install jupyterlab-topbar-extension && \
#    jupyter labextension install jupyterlab-system-monitor && \
RUN    jupyter labextension install @jupyter-widgets/jupyterlab-manager && \
    jupyter labextension install plotlywidget && \
    jupyter labextension install jupyterlab-plotly && \
    jupyter labextension install jupyterlab-plotly

# visual git manager
#RUN jupyter labextension install @jupyterlab/git && \
#    python3 -m pip install --upgrade jupyterlab-git && \
#    jupyter serverextension enable --py jupyterlab_git

# USER SETTINGS
RUN echo "export EDITOR=/usr/bin/vim" >> /home/jovyan/.bashrc
RUN echo "export PAGER=less" >> /home/jovyan/.bashrc

RUN jupyter nbextension enable snippets_menu/main && \
    jupyter nbextension enable codefolding/main && \
    jupyter nbextension enable codefolding/edit && \
    jupyter nbextension enable execute_time/ExecuteTime && \
    jupyter nbextension enable notify/notify && \
    jupyter nbextension enable rubberband/main && \
    jupyter nbextension enable varInspector/main && \
    jupyter nbextension enable latex_envs/latex_envs && \
    jupyter nbextension enable load_tex_macros/main && \
    jupyter nbextension enable toc2/main

# remember git login credentials
RUN git config --global credential.helper "cache --timeout 144000"
RUN echo "c.LatexConfig.latex_command = 'pdflatex'" >> /home/jovyan/.jupyter/jupyter_notebook_config.py

####### Octave #####
USER root

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        python3-sympy \
        octave \
        octave-symbolic \
        octave-miscellaneous \
        octave-io \
        octave-control \
        gnuplot \
        ghostscript

# Octave
USER $NB_UID

RUN conda install --quiet --yes \
    'octave_kernel'


###### R ENV #######
USER root

# R pre-requisites
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    fonts-dejavu \
    unixodbc \
    unixodbc-dev \
    r-cran-rodbc \
    gfortran \
    gcc && \
    rm -rf /var/lib/apt/lists/*

# Fix for devtools https://github.com/conda-forge/r-devtools-feedstock/issues/4
RUN ln -s /bin/tar /bin/gtar


# R pre-requisites
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    fonts-dejavu \
    unixodbc \
    unixodbc-dev \
    r-cran-rodbc \
    gfortran \
    gcc && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


USER $NB_UID
# R packages
RUN conda install --quiet --yes \
    'r-base=4.0.3' \
    'r-caret=6.*' \
    'r-crayon=1.4*' \
    'r-devtools=2.3*' \
    'r-forecast=8.13*' \
    'r-hexbin=1.28*' \
    'r-htmltools=0.5*' \
    'r-htmlwidgets=1.5*' \
    'r-irkernel=1.1*' \
    'r-nycflights13=1.0*' \
    'r-randomforest=4.6*' \
    'r-rcurl=1.98*' \
    'r-rmarkdown=2.6*' \
    'r-rodbc=1.3*' \
    'r-rsqlite=2.2*' \
    'r-shiny=1.6*' \
    'r-tidyverse=1.3*' \
    'unixodbc=2.3.*' \
    'r-tidymodels=0.1*'
RUN \
    conda clean --all -f -y && \
    fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"

# Install e1071 R package (dependency of the caret R package)
#RUN conda install --quiet --yes r-e1071


# RStudio
RUN python3 -m pip install jupyter-rsession-proxy
RUN cd /tmp/ && \
    git clone --depth 1 https://github.com/jupyterhub/jupyter-server-proxy && \
    cd jupyter-server-proxy/jupyterlab-server-proxy && \
    npm install && npm run build && jupyter labextension link . && \
    npm run build && jupyter lab build


# install rstudio-server
USER root
RUN apt-get update && \
    curl --silent -L --fail https://download2.rstudio.org/server/bionic/amd64/rstudio-server-1.4.1103-amd64.deb > /tmp/rstudio.deb && \
    apt-get install -y /tmp/rstudio.deb && \
    rm /tmp/rstudio.deb

ENV PATH=$PATH:/usr/lib/rstudio-server/bin

# I do not think these are necessary
#RUN apt-get update && \
#	apt-get install -y --no-install-recommends \
#		libapparmor1 \
#		libedit2 \
#		lsb-release \
#		psmisc \
#		libssl1.0.0 \
#		;

#RUN apt-get install gdebi-core
RUN curl --silent -L --fail https://download3.rstudio.org/ubuntu-14.04/x86_64/shiny-server-1.5.9.923-amd64.deb > /tmp/rshiny.deb && \
    apt-get install -y /tmp/rshiny.deb && \
    rm /tmp/rshiny.deb

# Cleanup
RUN rm -rf $CONDA_DIR/share/jupyter/lab/staging && \
    rm -rf /home/$NB_USER/.cache/yarn && \
    apt-get -qq purge && \
    apt-get -qq clean && \
    rm -rf /var/lib/apt/lists/*

USER $NB_UID

# Final cleaning
# build and clean up (for good measure)
RUN  npm cache clean --force && \
    rm -rf /home/$NB_USER/.node-gyp

RUN conda clean --all -f -y && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER

USER $NB_UID
RUN conda install poliastro --channel conda-forge --yes
RUN pip3 install --force-reinstall -U jupyter
#RUN conda create -y -n jupyterlab-debugger -c conda-forge jupyterlab=3 xeus-python
#RUN conda activate jupyterlab-debugger
RUN conda install xeus-python notebook -y -c conda-forge
