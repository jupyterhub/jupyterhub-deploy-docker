# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.
import os
import csv
import sys

from dockerspawner import DockerSpawner

from raven_auth.raven_auth import RavenAuthenticator


# Configuration file for JupyterHub

c.JupyterHub.log_level = 'DEBUG'

c = get_config()

# We rely on environment variables to configure JupyterHub so that we
# avoid having to rebuild the JupyterHub container every time we change a
# configuration parameter.

# Read Instructors and students.
pwd = os.path.dirname(__file__)
instructors = []

with open(os.path.join(pwd, 'instructors.csv'), 'r') as f:
    rdr = csv.DictReader(filter(lambda row: len(row.strip()) > 0 and row.strip()[0] != '#', f))
    for row in rdr:
        instructors.append(row)

students = []
with open(os.path.join(pwd, 'students.csv'), 'r') as f:
    rdr = csv.DictReader(filter(lambda row: len(row.strip()) > 0 and row.strip()[0] != '#', f))
    for row in rdr:
        students.append(row)

# Same uid and gid is used for all instructors, and similarly same uid and gid are used for all students.
# A linux user with the same uid as instructor_uid and with the same primary gid as instructor_gid should exist on the host machine.
# This linux account should be used by instructors to manage assignment files.
# Even though all students will have same id inside their separate docker containers. They won't be able to access each other's
# files because each of them will have different docker volumes mounted on their home directories inside container.
instructor_uid = os.environ['INSTRUCTOR_UID']
instructor_gid = os.environ['INSTRUCTOR_GID']
student_uid = os.environ['STUDENT_UID']
student_gid = os.environ['STUDENT_GID']

course_name = os.environ['COURSE_NAME']
notebook_dir_relative = os.environ['DOCKER_NOTEBOOK_DIR']

class VolumeCreatingSpawner(DockerSpawner):
    """
    DockerSpawner, but creates volumes
    """

    def start(self):
        directory = "/home/caelum/" + self.user.name
        if not os.path.exists(directory):
            os.makedirs(directory)
            os.chown(directory,1000,1000)
        return super().start()

    def get_env(self):
        env = super().get_env()
        env['NB_USER'] = env['NB_GROUP'] = self.user.name
        env['INSTRUCTOR_UID'] = instructor_uid
        env['INSTRUCTOR_GID'] = instructor_gid
        env['COURSE_NAME'] = course_name
        env['NOTEBOOK_DIR'] = notebook_dir_relative
        env['NBGRADER_DB_URL'] = 'postgresql://postgres:{password}@{host}/{db}'.format(
            host=os.environ['NBG_POSTGRES_HOST'],
            password=os.environ['NBG_POSTGRES_PASSWORD'],
            db=os.environ['NBG_POSTGRES_DB']
            )
        # Course home directory on container as setup by `singleuser/bin/start-custom.sh`
        env['COURSE_HOME_ON_CONTAINER'] = os.path.join('/home', env['NB_USER'], notebook_dir_relative, course_name)


# Spawn single-user servers as Docker containers
        for instructor in instructors:
            if instructor['id'] == self.user.name:
                env['IS_INSTRUCTOR'] = 'true'
                env['NB_UID'] = instructor_uid
                env['NB_GID'] = instructor_gid
                return env

        # Hub user is not instructor.
        env['IS_INSTRUCTOR'] = 'false'
        env['NB_UID'] = student_uid
        env['NB_GID'] = student_gid
        return env

c.JupyterHub.spawner_class = VolumeCreatingSpawner

c.DockerSpawner.container_image = os.environ['DOCKER_NOTEBOOK_IMAGE']
# We do nbgrade related stuff in `start_custom.sh`, so startup command is not customizable. It is hardcoded.
c.DockerSpawner.cmd = '/home/opam/.local/bin/start-custom.sh'

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
home_dir = '/home/{username}'
notebook_dir = os.path.join(home_dir, notebook_dir_relative)

c.DockerSpawner.notebook_dir = notebook_dir
# Mount the real user's Docker volume on the host to the notebook user's
# notebook directory in the container
c.DockerSpawner.volumes = { '/home/caelum/{username}': home_dir,
        'nb-grader-exchange' : '/srv/nbgrader/exchange',
        os.environ['COURSE_HOME'] : '/srv/nbgrader/%s' % course_name}

# volume_driver is no longer a keyword argument to create_container()
# c.DockerSpawner.extra_create_kwargs.update({ 'volume_driver': 'local' })
# Remove containers once they are stopped
c.DockerSpawner.remove_containers = True
# For debugging arguments passed to spawned containers
c.DockerSpawner.debug = True

c.DockerSpawner.mem_limit = '2G'
c.DockerSpawner.http_timeout = 60
c.DockerSpawner.start_timeout = 60

# User containers will access hub by container name on the Docker network
c.JupyterHub.hub_ip = '0.0.0.0'
c.JupyterHub.hub_port = 8080
c.JupyterHub.hub_connect_ip = 'jupyterhub'


# TLS config
#c.JupyterHub.port = 443
#c.JupyterHub.ssl_key = os.environ['SSL_KEY']
#c.JupyterHub.ssl_cert = os.environ['SSL_CERT']

# Choose an authentication method: github or raven or dummy

# Authenticate users with GitHub OAuth
# c.JupyterHub.authenticator_class = 'oauthenticator.GitHubOAuthenticator'
# c.GitHubOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']

# Authenticate users with Raven
c.JupyterHub.authenticator_class = RavenAuthenticator
c.RavenAuthenticator.description = "FoCS JupyterHub"
c.RavenAuthenticator.long_description = "Welcome to the Foundations of Computer Science Jupyterhub server. This is a resource for students taking the 1A Computer Science course 'Foundations of Computer Science' and is not intended as a general purpose JupyterHub Server."
c.RavenAuthenticator.login_logo="/opt/conda/lib/python3.6/site-packages/raven_auth/files/origami-camel.png"
c.RavenAuthenticator.ssl=True

#c.JupyterHub.authenticator_class = 'dummyauthenticator.DummyAuthenticator'
#c.DummyAuthenticator.password = "password"

#c.ConfigurableHTTPProxy.command = ['configurable-http-proxy', '--redirect-port', '80']
c.ConfigurableHTTPProxy.should_start = False
c.ConfigurableHTTPProxy.auth_token = os.environ['CONFIGPROXY_AUTH_TOKEN']
c.ConfigurableHTTPProxy.api_url='http://chp:8081/'
c.JupyterHub.cleanup_servers = False

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
c.Authenticator.admin_users = admin = set()
c.Authenticator.whitelist = whitelist = set()
c.JupyterHub.admin_access = True

for instructor in instructors:
    admin.add(instructor['id'])
    whitelist.add(instructor['id'])

for student in students:
    whitelist.add(student['id'])

#c.Authenticator.github_organization_whitelist = set(['ocamllabs','owlbarn','tarides','ocaml','pkp-neuro'])

# Templates
c.JupyterHub.template_paths = ['/srv/jupyterhub/templates/']

c.JupyterHub.services = [
    {
    'name': 'cull-idle',
    'admin': True,
    'command': [sys.executable, '/srv/jupyterhub/cull_idle_servers.py', '--timeout=3600'],
    }
]

