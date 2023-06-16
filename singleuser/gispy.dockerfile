ARG DOCKER_NOTEBOOK_IMAGE
FROM $DOCKER_NOTEBOOK_IMAGE
ARG JUPYTERHUB_VERSION
RUN python3 -m pip install --no-cache jupyterhub==$JUPYTERHUB_VERSION

USER root

RUN apt-get update                      && \
    apt-get install -y libgl1-mesa-glx  \
                        libjpeg9        \
                        libjpeg9-dev    && \
    apt-get install -y python3-pip      \
                        build-essential \
                        curl            \
                        sudo            \
                        tzdata          \
                        git-core        \
                        # libproj-dev     \
                        # libgeos-dev     \
                        vim             && \
    rm -rf /var/lib/apt/lists/*         && \
    apt-get clean                       && \
    apt-get autoremove -y

USER $NB_UID

RUN mamba install -y -c conda-forge \
                        fiona \
                        geopandas \
                        geoplot \
                        holoviews \
                        hvplot \
                        ipython \
                        kalasiris \
                        matplotlib \
                        numpy \
                        plotly \
                        pygeos \
                        pyproj \
                        rasterio \
                        rioxarray \
                        scikit-image \
                        scipy \
                        shapely \
                        spectral
