# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
ARG JUPYTERHUB_VERSION
FROM jupyterhub/jupyterhub:$JUPYTERHUB_VERSION

# Guarantee pip is up-to-date
RUN python3 -m pip install --no-cache --upgrade \
      setuptools \
      pip

# Install dockerspawner, nativeauthenticator
RUN python3 -m pip install --no-cache-dir \
        dockerspawner==12.* \
        jupyterhub-nativeauthenticator==1.* \
        oauthenticator==15.*

CMD ["jupyterhub", "-f", "/srv/jupyterhub/jupyterhub_config.py"]
