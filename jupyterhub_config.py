# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# Configuration file for JupyterHub
import os
import csv


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


from dockerspawner import DockerSpawner

# We extend DockerSpawner to set user name, user ids etc. on environment variables.
# These env variables are used by `singleuser/bin/start-custom.sh` to create appropriate users, manage file permissions etc.
class MyDockerSpawner(DockerSpawner):
    def get_env(self):
        env = super().get_env()
        env['NB_USER'] = env['NB_GROUP'] = self.user.name
        env['INSTRUCTOR_UID'] = instructor_uid
        env['INSTRUCTOR_GID'] = instructor_gid
        env['COURSE_NAME'] = course_name
        env['NOTEBOOK_DIR'] = notebook_dir_relative
        # Course home directory on container as setup by `singleuser/bin/start-custom.sh`
        env['COURSE_HOME_ON_CONTAINER'] = os.path.join('/home', env['NB_USER'], notebook_dir_relative, course_name)

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

# Spawn single-user servers as Docker containers
c.JupyterHub.spawner_class = MyDockerSpawner

# We do nbgrade related stuff in `start_custom.sh`, so startup command is not customizable. It is hardcoded.
c.DockerSpawner.cmd = 'start-custom.sh'
# Spawn containers from this image
c.DockerSpawner.container_image = os.environ['DOCKER_NOTEBOOK_IMAGE']

# Following two lines have to be commented out after upgrade to JupyterHub 0.8.0. 
# Otherwise c.DockerSpawner.notebook_dir doesn't work. Single user servers always start at home directory.
# spawn_cmd = os.environ.get('DOCKER_SPAWN_CMD', "start-singleuser.sh")
# c.DockerSpawner.extra_create_kwargs.update({ 'command': spawn_cmd })

# Connect containers to this Docker network
network_name = os.environ['DOCKER_NETWORK_NAME']
c.DockerSpawner.use_internal_ip = True
c.DockerSpawner.network_name = network_name
# Pass the network name as argument to spawned containers
c.DockerSpawner.extra_host_config = { 'network_mode': network_name }

# Explicitly set notebook directory.
home_dir = '/home/{username}'
notebook_dir = os.path.join(home_dir, notebook_dir_relative)
c.DockerSpawner.notebook_dir = notebook_dir

# Mount the user's Docker volume on the host to the home directory in the container.
# Mount a volume to be used as nbgrader exchange directory. Same volume must be mounted on docker containers for all users.
# Mount the course home directory on the docker container for the user. The same directory should be mounted on docker containers for different users.
# Also make sure that permissions are properly set on various subdirectories in the course home so that any student doesn't get access to solutions.
# Students should also not be able to see someone's else solutions or grades.
c.DockerSpawner.volumes = { 'jupyterhub-user-{username}': home_dir , 
        'nbgrader-exchange' : '/srv/nbgrader/exchange', 
        os.environ['COURSE_HOME'] : '/srv/nbgrader/%s' % course_name}

c.DockerSpawner.extra_create_kwargs.update({ 'volume_driver': 'local' })
# Remove containers once they are stopped
c.DockerSpawner.remove_containers = True
# For debugging arguments passed to spawned containers
c.DockerSpawner.debug = True

# User containers will access hub by container name on the Docker network
c.JupyterHub.hub_ip = 'jupyterhub'
c.JupyterHub.hub_port = 8080

# TLS config
c.JupyterHub.port = 443
c.JupyterHub.ssl_key = os.environ['SSL_KEY']
c.JupyterHub.ssl_cert = os.environ['SSL_CERT']

# Authenticate users with GitHub OAuth
c.JupyterHub.authenticator_class = 'oauthenticator.GitHubOAuthenticator'
c.GitHubOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']

# Persist hub data on volume mounted inside container
data_dir = os.environ.get('DATA_VOLUME_CONTAINER', '/data')

c.JupyterHub.cookie_secret_file = os.path.join(data_dir,
    'jupyterhub_cookie_secret')

c.JupyterHub.db_url = 'postgresql://postgres:{password}@{host}/{db}'.format(
    host=os.environ['POSTGRES_HOST'],
    password=os.environ['POSTGRES_PASSWORD'],
    db=os.environ['POSTGRES_DB'],
)

# Whitlelist students and instructors.
# Makes all instructors as admins.
c.Authenticator.whitelist = whitelist = set()
c.Authenticator.admin_users = admin = set()
c.JupyterHub.admin_access = True
for instructor in instructors:
    admin.add(instructor['id'])
    whitelist.add(instructor['id'])

for student in students:
    whitelist.add(student['id'])

