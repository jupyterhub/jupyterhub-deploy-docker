# The jupyterhub/jupyterhub instance is quite bulky... A stripped down version
# can be built from the python:3.x-slim images.
#FROM jupyterhub/jupyterhub
FROM python:3.11-slim

# Recommended minimal set of packages, allowing use of DockerSpawner
# and OAuthenticator classes.
# hadolint ignore=DL3008,DL3013
RUN apt-get update && \
    apt-get install -y git --no-install-recommends && \
    python3 -m pip install -U --no-cache-dir \
        dockerspawner \
        jupyterhub \
        oauthenticator \
        git+https://github.com/jupyterhub/traefik-proxy.git && \
    apt-get remove -y git && \
    rm -rf /var/lib/apt/lists

CMD ["jupyterhub", "-f", "/srv/jupyterhub/jupyterhub_config.py"]
WORKDIR /srv/jupyterhub
