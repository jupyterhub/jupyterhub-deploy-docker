# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# Configuration file for JupyterHub
c = get_config()

import os

# We rely on environment variables to configure JupyterHub so that we
# avoid having to rebuild the JupyterHub container every time we change a
# configuration parameter.

import sys
import importlib.util

this_dir = os.path.dirname(__file__)
file_path = os.path.join(this_dir, 'custom_spawner.py')
module_name = 'custom_spawner'

if os.path.exists(file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    # module = importlib.util.module_from_spec(spec)
    custom_spawner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(custom_spawner)

else:
    import glob
    print(file_path)
    print(glob.glob(os.path.join(os.getcwd(), '*')))

# from importlib import import_module
# custom_spawner = import_module('custom_spawner')

# Spawn single-user servers as Docker containers
# c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
c.JupyterHub.spawner_class = custom_spawner.CustomDockerSpawner

# Spawn containers from this image
c.DockerSpawner.image = os.environ['DOCKER_NOTEBOOK_IMAGE']

# JupyterHub requires a single-user instance of the Notebook server, so we
# default to using the `start-singleuser.sh` script included in the
# jupyter/docker-stacks *-notebook images as the Docker run command when
# spawning containers.  Optionally, you can override the Docker run command
# using the DOCKER_SPAWN_CMD environment variable.
spawn_cmd = os.environ.get('DOCKER_SPAWN_CMD', "start-singleuser.sh")
c.DockerSpawner.extra_create_kwargs.update({ 'command': spawn_cmd })

# Connect containers to this Docker network
c.DockerSpawner.network_name = os.environ['DOCKER_NETWORK_NAME']
# Pass the network name as argument to spawned containers
c.DockerSpawner.extra_host_config = {
    'network_mode': os.environ['DOCKER_NETWORK_NAME']
}
c.DockerSpawner.use_internal_ip = True

# Explicitly set notebook directory because we'll be mounting a host volume to
# it.  Most jupyter/docker-stacks *-notebook images run the Notebook server as
# user `jovyan`, and set the notebook directory to `/home/jovyan/work`.
# We follow the same convention.
notebook_dir = os.environ.get('NOTEBOOK_DIR', '/home/jovyan')
c.DockerSpawner.notebook_dir = notebook_dir

# Mount the real user's Docker volume on the host to the notebook user's
# notebook directory in the container
# notebook_dir_host = os.environ.get('LOCAL_NOTEBOOK_DIR', 'jupyterhub-user-{username}')
work_dir_host = os.environ['NOTEBOOK_WORK_DIRBASE_HOST'] + '/{username}'
work_dir_container = os.environ['NOTEBOOK_WORK_DIR']

c.DockerSpawner.volumes = {
    work_dir_host: work_dir_container,
    os.environ['NOTEBOOK_DATA_DIR_HOST']: os.environ['NOTEBOOK_DATA_DIR'],
    os.environ['NOTEBOOK_SHARED_DIR_HOST']: os.environ['NOTEBOOK_SHARED_DIR'],
    os.environ['NOTEBOOK_ISISDATA_DIR_HOST']: os.environ['NOTEBOOK_ISISDATA_DIR']
}

# volume_driver is no longer a keyword argument to create_container()
# c.DockerSpawner.extra_create_kwargs.update({ 'volume_driver': 'local' })

# Remove containers once they are stopped
c.DockerSpawner.remove = True
# For debugging arguments passed to spawned containers
c.DockerSpawner.debug = True

# c.DockerSpawner.extra_create_kwargs.update({'user': 'root'})
c.DockerSpawner.extra_create_kwargs = {'user': 'root'}

c.DockerSpawner.environment = {
    "CHOWN_HOME": "yes",
    "CHOWN_EXTRA": work_dir_container,
    "CHOWN_HOME_OPTS": "-R",
    "NB_UID": 999,
    "NB_GID": 100,

    "WORK_DIR": work_dir_container,
    "DATA_DIR": os.environ['NOTEBOOK_DATA_DIR'],
    "ISISDATA_DIR": os.environ['NOTEBOOK_ISISDATA_DIR']
}

# User containers will access hub by container name on the Docker network
# c.JupyterHub.hub_ip = os.environ.get('DOCKER_MACHINE_NAME', 'jupyterhub')
c.JupyterHub.hub_ip = os.environ['DOCKER_MACHINE_NAME']
#c.JupyterHub.hub_port = 8080
c.JupyterHub.hub_port = 8999

c.JupyterHub.port = int(os.environ['JUPYTERHUB_PORT'])
# TLS config
# c.JupyterHub.port = 443
# c.JupyterHub.ssl_key = os.environ['SSL_KEY']
# c.JupyterHub.ssl_cert = os.environ['SSL_CERT']

# # Authenticate users with GitHub OAuth
# c.JupyterHub.authenticator_class = 'oauthenticator.GitHubOAuthenticator'
# c.GitHubOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']
# Authenticator
if 'GITLAB_HOST' in os.environ:
    from oauthenticator.gitlab import GitLabOAuthenticator
    c.JupyterHub.authenticator_class = GitLabOAuthenticator

else:
    # from jupyterhub.auth import PAMAuthenticator
    # c.JupyterHub.authenticator_class = PAMAuthenticator
    from jupyterhub.auth import DummyAuthenticator
    c.JupyterHub.authenticator_class = DummyAuthenticator

    # Whitlelist users and admins
    whitelist = set()
    admin = set()
    pwd = os.path.dirname(__file__)
    try:
        with open(os.path.join(pwd, 'userlist'), 'r') as f:
            for line in f:
                if not line:
                    continue
                parts = line.split()
                # in case of newline at the end of userlist file
                if len(parts) >= 1:
                    name = parts[0]
                    whitelist.add(name)
                    if len(parts) > 1 and parts[1] == 'admin':
                        admin.add(name)

    except:
        whitelist.add('jovyan')
        admin.add('jovyan')

    else:
        c.Authenticator.allowed_users = whitelist
        c.Authenticator.admin_users = admin

    finally:
        c.JupyterHub.admin_access = True


# Persist hub data on volume mounted inside container
c.JupyterHub.cookie_secret_file = os.path.join(
    os.environ['DATA_VOLUME_CONTAINER'], 'jupyterhub_cookie_secret'
    )

# Db config
c.JupyterHub.db_url = 'postgresql://postgres:{password}@{host}/{db}'.format(
    host=os.environ['POSTGRES_HOST'],
    password=os.environ['POSTGRES_PASSWORD'],
    db=os.environ['POSTGRES_DB'],
)
