# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
# Major edits by MathematicalMichael(.com) 02-2019

# Configuration file for JupyterHub
import os
from subprocess import check_call
pwd = os.path.dirname(__file__)
c = get_config()
hub_name = os.environ['HUB_NAME']
c.NotebookApp.nbserver_extensions = {
    'jupyterlab_git': True,
} 

# Spawner dropdown menu?
enable_options=True
c.NotebookApp.allow_remote_access = True
# We rely on environment variables to configure JupyterHub so that we
# avoid having to rebuild the JupyterHub container every time we change a
# configuration parameter.

# Spawn single-user servers as Docker containers
#c.JupyterHub.spawner_class = spawner = 'dockerspawner.DockerSpawner'
from dockerspawner import DockerSpawner
class MyDockerSpawner(DockerSpawner):
    group_map = {}
    with open(os.path.join(pwd, 'userlist')) as f:
        for line in f:
            if not line:
                continue
            parts = line.split()
            # in case of newline at the end of userlist file
            if len(parts) >= 1:
                user_name = parts[0]
                group_map[user_name] = []

                for i in range(1,len(parts)):
                    group_id = parts.pop()
                    group_map[user_name].append(group_id)
    def start(self):
        if self.user.name in self.group_map:
            group_list = self.group_map[self.user.name]
            # add team volume to volumes
            for group_id in group_list: # admins in userlist get to write files.
                if group_id != 'admin':
                    self.volumes['%s/jupyterlab_settings'%(os.environ['HUB_LOC'])] = \
                        { 'bind': '/home/jovyan/.jupyter/lab/user-settings/@jupyterlab', 'mode': 'rw' }
                    if 'admin' in group_list: 
                        self.volumes['shared-{}'.format(group_id)] = \
                            { 'bind': '/home/jovyan/%s'%(group_id),
                                'mode': 'rw' } # or ro for read-only
                    else: # this "shared-" is part of the naming convention
                        self.volumes['shared-{}'.format(group_id)] = \
                            {'bind': '/home/jovyan/%s'%(group_id),
                                'mode': 'ro' } # or rw for write (can cause conflicts)
                else: # if admin is one of the groups in userlist, mount the following:
                    self.volumes['%s/userlist'%(os.environ['HUB_LOC'])] = \
                        { 'bind': '/home/jovyan/userlist', 'mode': 'rw' }
                    self.volumes['%s/jupyterhub_config.py'%(os.environ['HUB_LOC'])] = \
                        { 'bind': '/home/jovyan/jupyterhub_config.py', 'mode': 'rw' }
        self.environment['JUPYTER_ENABLE_LAB'] = 'yes'
        return super().start()

c.JupyterHub.spawner_class = MyDockerSpawner

# define some task to do on startup

# Spawn containers from this image (or a whitelist)
#c.DockerSpawner.image = "jupyter/datascience-notebook:7254cdcfa22b"
c.DockerSpawner.image = '%s-user'%hub_name
c.DockerSpawner.name_template = '%s-{username}_{servername}_{imagename}'%hub_name
if enable_options:
    # if whitelist enabled, the .container_image will be ignored in favor of the options below:
    c.DockerSpawner.image_whitelist = {'DEFAULT: math-user': c.DockerSpawner.image , 
                                     'RStudio': 'rstudio',
                                     'TeX': 'tex',
                                     'Python: minimal': 'python-min',
                                     'Python: tflow pro': 'python-tflow-pro',
                                     'Python: minimal pro': 'python-min-pro',
                                     'Python: minimal hook': 'python-min-entry',
                                     'Python: minimal pro hook': 'python-min-pro-entry',
                                     'Python: minimal pro hook tex': 'python-min-pro-entry-tex',
                                     'scipy-notebook': "jupyter/scipy-notebook", 
                                     'datascience-notebook': "jupyter/datascience-notebook",
                                     'tensorflow-notebook': "jupyter/tensorflow-notebook",
                                     'r-notebook': 'jupyter/r-notebook',
                                     'base-notebook': "jupyter/base-notebook"
                                      }
c.DockerSpawner.extra_host_config = {
    'cpuset': 0.1
}
# JupyterHub requires a single-user instance of the Notebook server, so we
# default to using the `start-singleuser.sh` script included in the
# jupyter/docker-stacks *-notebook images as the Docker run command when
# spawning containers.  Optionally, you can override the Docker run command
# using the DOCKER_SPAWN_CMD environment variable.
spawn_cmd = os.environ.get('DOCKER_SPAWN_CMD', "start-singleuser.sh")
c.DockerSpawner.extra_create_kwargs.update({ 'command': spawn_cmd })

# Memory limit
c.Spawner.mem_limit = '100G'  # RAM limit
#c.Spawner.cpu_limit = 0.1

# Connect containers to this Docker network
network_name = '%s-network'%hub_name
c.DockerSpawner.use_internal_ip = True
c.DockerSpawner.network_name = network_name
# Pass the network name as argument to spawned containers
c.DockerSpawner.extra_host_config = { 'network_mode': network_name }

# Explicitly set notebook directory because we'll be mounting a host volume to
# it.  Most jupyter/docker-stacks *-notebook images run the Notebook server as
# user `jovyan`, and set the notebook directory to `/home/jovyan/work`.
# We follow the same convention.
notebook_dir = os.environ.get('DOCKER_NOTEBOOK_DIR') or '/home/jovyan/work'
#c.DockerSpawner.notebook_dir = notebook_dir
# Mount the real user's Docker volume on the host to the notebook user's
# notebook directory in the container
c.DockerSpawner.volumes = { 'hub-user-{username}': notebook_dir }

# volume_driver is no longer a keyword argument to create_container()
# c.DockerSpawner.extra_create_kwargs.update({ 'volume_driver': 'local' })


# Remove containers once they are stopped
c.DockerSpawner.remove_containers = True
# For debugging arguments passed to spawned containers
c.DockerSpawner.debug = True


# User containers will access hub by container name on the Docker network
c.JupyterHub.hub_ip = hub_name
# The hub will be hosted at example.com/HUB_NAME/ 
c.JupyterHub.base_url = u'/%s/'%hub_name
#c.JupyterHub.hub_port = 8001

## Authentication 
# Whitlelist users and admins
c.Authenticator.whitelist = whitelist = set()
c.Authenticator.admin_users = admin = set()

# add default user so that first-time log in is easy.
admin.add('hub-admin')

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


# Authenticate users with GitHub OAuth
# c.JupyterHub.authenticator_class = 'oauthenticator.GitHubOAuthenticator'
# c.GitHubOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']

# Authenticate with thedataincubator/jupyterhub-hashauthenticator
c.JupyterHub.authenticator_class = 'hashauthenticator.HashAuthenticator'
# You can generate a good "secret key" by running `openssl rand -hex 32` in terminal.
# it is recommended to do this from time-to-time to change passwords (including changing their length)
c.HashAuthenticator.secret_key = os.environ['HASH_SECRET_KEY']  # Defaults to ''
c.HashAuthenticator.password_length = int(os.environ['PASSWORD_LENGTH'])          # Defaults to 6
# Can find your password by looking at `hashauthpw --length 10 [username] [key]`
# If the `show_logins` option is set to `True`, a CSV file containing 
#login names and passwords will be served (to admins only) at `/hub/login_list`. 
c.HashAuthenticator.show_logins = True            # Optional, defaults to False

# TLS config
#c.JupyterHub.port = 8000
#c.JupyterHub.ssl_key = os.environ['SSL_KEY']
#c.JupyterHub.ssl_cert = os.environ['SSL_CERT']

### Database Interaction - cookies, db for jupyterhub
# Persist hub data on volume mounted inside container
data_dir = '/data' # DATA_VOLUME_CONTAINER

c.JupyterHub.cookie_secret_file = os.path.join(data_dir,
    'jupyterhub_cookie_secret')

c.JupyterHub.db_url = 'postgresql://postgres:{password}@{host}/{db}'.format(
    host=os.environ['POSTGRES_HOST'],
    password=os.environ['POSTGRES_PASSWORD'],
    db=hub_name,
)

# Allow admin users to log into other single-user servers (e.g. for debugging, testing)?  As a courtesy, you should make sure your users know if admin_access is enabled.
c.JupyterHub.admin_access = True

## Allow named single-user servers per user
c.JupyterHub.allow_named_servers = True

# Run script to automatically stop idle single-user servers as a jupyterhub service.
#c.JupyterHub.services = [
#    {
#        'name': 'cull_idle',
#        'admin': True,
#        'command': 'python /srv/jupyterhub/cull_idle_servers.py --timeout=3600'.split(),
#    },
#]
