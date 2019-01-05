# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# Configuration file for JupyterHub
import os

c = get_config()

# We rely on environment variables to configure JupyterHub so that we
# avoid having to rebuild the JupyterHub container every time we change a
# configuration parameter.

# Spawn single-user servers as Docker containers
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
# Spawn containers from this image (or a whitelist)
#c.DockerSpawner.container_image = "jupyter/datascience-notebook:7254cdcfa22b"
c.DockerSpawner.container_image = os.environ['DOCKER_NOTEBOOK_IMAGE']
enable_options=False
if enable_options:
    # if whitelist enabled, the .container_image will be ignored in favor of the options below:
    c.DockerSpawner.image_whitelist = {'fenics': "jupyterhub-user", 
                                     'scipy-notebook': "jupyter/scipy-notebook", 
                                     'datascience-notebook': "jupyter/datascience-notebook",
                                     'r-notebook': 'jupyter/r-notebook',
                                     'base-notebook': "jupyter/base-notebook",
                                     'RStudio': 'rstudio'}

# JupyterHub requires a single-user instance of the Notebook server, so we
# default to using the `start-singleuser.sh` script included in the
# jupyter/docker-stacks *-notebook images as the Docker run command when
# spawning containers.  Optionally, you can override the Docker run command
# using the DOCKER_SPAWN_CMD environment variable.
spawn_cmd = os.environ.get('DOCKER_SPAWN_CMD', "start-singleuser.sh")
c.DockerSpawner.extra_create_kwargs.update({ 'command': spawn_cmd })

# Memory limit
c.Spawner.mem_limit = '2G'  # RAM limit

# Connect containers to this Docker network
network_name = os.environ['DOCKER_NETWORK_NAME']
c.DockerSpawner.use_internal_ip = True
c.DockerSpawner.network_name = network_name
# Pass the network name as argument to spawned containers
c.DockerSpawner.extra_host_config = { 'network_mode': network_name }

# Explicitly set notebook directory because we'll be mounting a host volume to
# it.  Most jupyter/docker-stacks *-notebook images run the Notebook server as
# user `jovyan`, and set the notebook directory to `/home/jovyan/work`.
# We follow the same convention.
notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/jovyan/work'
c.DockerSpawner.notebook_dir = notebook_dir
# Mount the real user's Docker volume on the host to the notebook user's
# notebook directory in the container

# c.DockerSpawner.volumes = { 'jupyterhub-user-{username}': notebook_dir }
c.DockerSpawner.volumes = { 'hub-user-{username}': notebook_dir, 
                            'ro_shared_volume':{"bind": '/home/jovyan/shared_volume_ro', "mode": "ro"},
                            'rw_shared_volume':{"bind": '/home/jovyan/shared_volume_rw', "mode": "rw", "propagation": "rshared"},
                            '/home/shared/':'/home/jovyan/shared_directory/' } 

# volume_driver is no longer a keyword argument to create_container()
# c.DockerSpawner.extra_create_kwargs.update({ 'volume_driver': 'local' })
# Remove containers once they are stopped
c.DockerSpawner.remove_containers = True
# For debugging arguments passed to spawned containers
c.DockerSpawner.debug = True

# User containers will access hub by container name on the Docker network
c.JupyterHub.hub_ip = 'jupyterhub'
#c.JupyterHub.hub_port = 8001

# TLS config
#c.JupyterHub.port = 8000
#c.JupyterHub.ssl_key = os.environ['SSL_KEY']
#c.JupyterHub.ssl_cert = os.environ['SSL_CERT']

### Authentication 
# Authenticate users with GitHub OAuth
# c.JupyterHub.authenticator_class = 'oauthenticator.GitHubOAuthenticator'
# c.GitHubOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']

# Authenticate with thedataincubator/jupyterhub-hashauthenticator
c.JupyterHub.authenticator_class = 'hashauthenticator.HashAuthenticator'
# You can generate a good "secret key" by running `openssl rand -hex 32` in terminal.
# it is recommended to do this from time-to-time to change passwords (including changing their length)
c.HashAuthenticator.secret_key = os.environ['HASH_SECRET_KEY']  # Defaults to ''
c.HashAuthenticator.password_length = 6          # Defaults to 6
# Can find your password by looking at `hashauthpw --length 10 [username] [key]`
# If the `show_logins` option is set to `True`, a CSV file containing 
#login names and passwords will be served (to admins only) at `/hub/login_list`. 
c.HashAuthenticator.show_logins = True            # Optional, defaults to False


### Database Interaction - cookies, db for jupyterhub
# Persist hub data on volume mounted inside container
data_dir = os.environ.get('DATA_VOLUME_CONTAINER', '/data')

c.JupyterHub.cookie_secret_file = os.path.join(data_dir,
    'jupyterhub_cookie_secret')

c.JupyterHub.db_url = 'postgresql://postgres:{password}@{host}/{db}'.format(
    host=os.environ['POSTGRES_HOST'],
    password=os.environ['POSTGRES_PASSWORD'],
    db=os.environ['POSTGRES_DB'],
)

# Whitlelist users and admins
c.Authenticator.whitelist = whitelist = set()
c.Authenticator.admin_users = admin = set()
c.JupyterHub.admin_access = True
pwd = os.path.dirname(__file__)
with open(os.path.join(pwd, 'userlist')) as f:
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

# Run script to automatically stop idle single-user servers as a jupyterhub service.
c.JupyterHub.services = [
    {
        'name': 'cull_idle',
        'admin': True,
        'command': 'python /srv/jupyterhub/cull_idle_servers.py --timeout=3600'.split(),
    },
]
