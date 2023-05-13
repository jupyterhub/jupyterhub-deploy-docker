# The jupyterhub/jupyterhub instance is quite bulky... A stripped down version
# can be built from the python:3.x-slim images.
#FROM jupyterhub/jupyterhub
FROM python:3.11-slim

# Recommended minimal set of packages, allowing use of DockerSpawner
# and OAuthenticator classes.
RUN apt update && \
    apt install -y git && \
    pip3 install -U --no-cache \
        dockerspawner \
        jupyterhub \
        oauthenticator \
        git+https://github.com/jupyterhub/traefik-proxy.git && \
    apt remove -y git && \
    rm -rf /var/lib/apt/lists

CMD jupyterhub -f /srv/jupyterhub/jupyterhub_config.py
WORKDIR /srv/jupyterhub

