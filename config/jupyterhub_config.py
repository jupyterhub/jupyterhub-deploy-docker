# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# Configuration file for JupyterHub
import os
import sys

c = get_config()

this_dir = os.path.dirname(__file__)

# We rely on environment variables to configure JupyterHub so that we
# avoid having to rebuild the JupyterHub container every time we change a
# configuration parameter.

# Import ancillary modules
def import_file(file_path, module_name):
    """Return module object from file_path (.py) with module_name"""
    import importlib.util

    assert os.path.exists(file_path), file_path
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    # module = importlib.util.module_from_spec(spec)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


## Import Custom Spawner class(es)
module_name = "custom_spawner"
file_path = os.path.join(this_dir, f"{module_name}.py")
custom_spawner = import_file(file_path, module_name)

# Spawn single-user servers as Docker containers
# c.JupyterHub.spawner_class = "dockerspawner.DockerSpawner"
c.JupyterHub.spawner_class = custom_spawner.CustomDockerSpawner

# Spawn containers from this image
c.DockerSpawner.image = os.environ.get(
    "DOCKER_NOTEBOOK_IMAGE", "jupyter/minimal-notebook:latest"
)

# JupyterHub requires a single-user instance of the Notebook server, so we
# default to using the `start-singleuser.sh` script included in the
# jupyter/docker-stacks *-notebook images as the Docker run command when
# spawning containers.  Optionally, you can override the Docker run command
# using the DOCKER_SPAWN_CMD environment variable.
spawn_cmd = os.environ.get("DOCKER_SPAWN_CMD", "start-singleuser.sh")
c.DockerSpawner.cmd = spawn_cmd

# Connect containers to this Docker network
network_name = os.environ["DOCKER_NETWORK_NAME"]
c.DockerSpawner.network_name = network_name
c.DockerSpawner.use_internal_ip = True

# Explicitly set notebook directory because we'll be mounting a volume to it.
# Most jupyter/docker-stacks *-notebook images run the Notebook server as
# user `jovyan`, and set the notebook directory to `/home/jovyan/work`.
# We follow the same convention.
notebook_dir = os.environ.get("DOCKER_NOTEBOOK_DIR") or "/home/jovyan"
c.DockerSpawner.notebook_dir = notebook_dir

# Mount the real user's Docker volume on the host to the notebook user's
# notebook directory in the container
# local_work_basedir = os.environ.get('LOCAL_WORK_BASEDIR', 'jupyterhub-user-{username}')
_default_local_volumes_basedir = "/tmp/jupyterhub/data-notebook-server"

docker_work_dir = notebook_dir + "/work"
local_work_basedir = os.environ.get(
    "LOCAL_WORK_BASEDIR", _default_local_volumes_basedir + "/work"
)
local_work_dir = local_work_basedir + "/{username}"

docker_data_dir = "/mnt/data"
local_data_dir = os.environ.get(
    "LOCAL_DATA_DIR", _default_local_volumes_basedir + "/data"
)

docker_shared_dir = notebook_dir + "/shared"
local_shared_dir = os.environ.get(
    "LOCAL_SHARED_DIR", _default_local_volumes_basedir + "/shared"
)

docker_isisdata_dir = "/mnt/isis/data"
local_isisdata_dir = os.environ.get(
    "LOCAL_ISISDATA_DIR", _default_local_volumes_basedir + "/isisdata"
)

c.DockerSpawner.volumes = {
    local_work_dir: docker_work_dir,
    local_data_dir: docker_data_dir,
    local_shared_dir: docker_shared_dir,
    local_isisdata_dir: docker_isisdata_dir,
}

c.DockerSpawner.extra_create_kwargs.update({"user": "root"})
# c.DockerSpawner.extra_create_kwargs = {'user': 'root'}

c.DockerSpawner.environment = {
    "CHOWN_HOME": "yes",
    "CHOWN_EXTRA": docker_work_dir,
    "CHOWN_HOME_OPTS": "-R",
    "NB_UID": 999,
    "NB_GID": 100,
    "WORK_DIR": docker_work_dir,
    "DATA_DIR": docker_data_dir,
    "ISISDATA_DIR": docker_isisdata_dir,
}

# Remove containers once they are stopped
c.DockerSpawner.remove = True

# For debugging arguments passed to spawned containers
c.DockerSpawner.debug = True

# User containers will access hub by container name on the Docker network
c.JupyterHub.hub_ip = "jupyterhub"
c.JupyterHub.hub_port = 8080

# Persist hub data on volume mounted inside container
c.JupyterHub.cookie_secret_file = "/data/jupyterhub_cookie_secret"
c.JupyterHub.db_url = "sqlite:////data/jupyterhub.sqlite"

try:
    # Authenticate users with OAuth authenticator
    # If 'OAUTHENTICATOR' not defined in Env, throws error and falls back to Native
    if os.environ["OAUTHENTICATOR"].upper() == "GITLAB":
        from oauthenticator.gitlab import GitLabOAuthenticator

        c.JupyterHub.authenticator_class = GitLabOAuthenticator
    elif os.environ["OAUTHENTICATOR"].upper() == "GITHUB":
        from oauthenticator.github import GitHubOAuthenticator

        c.JupyterHub.authenticator_class = GitHubOAuthenticator
    else:
        raise ValueError("Expected 'gitlab' or 'github' for OAUTHENTICATOR")

except:
    # Authenticate users with Native Authenticator
    c.JupyterHub.authenticator_class = "nativeauthenticator.NativeAuthenticator"
    # Allow anyone to sign-up without approval
    c.NativeAuthenticator.open_signup = True

# # Allowed admins
# admin = os.environ.get("JUPYTERHUB_ADMIN")
# if admin:
#     c.Authenticator.admin_users = [admin]

# Whitlelist users and admins
whitelist = set()
admin = set()
try:
    with open(os.path.join(this_dir, "userlist"), "r") as f:
        for line in f:
            if not line:
                continue
            parts = line.split()
            # in case of newline at the end of userlist file
            if len(parts) >= 1:
                name = parts[0]
                whitelist.add(name)
                if len(parts) > 1 and parts[1] == "admin":
                    admin.add(name)
except:
    whitelist.add("jovyan")
    admin.add("jovyan")
else:
    c.Authenticator.allowed_users = whitelist
    c.Authenticator.admin_users = admin
finally:
    c.JupyterHub.admin_access = True
