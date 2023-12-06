# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# =================================
# Configuration file for JupyterHub
# =================================

import os
import sys

_THISDIR = os.path.dirname(__file__)

# Auxiliary functions
# ---

# Import "module.py" in this directory (for instance, 'custom_spawner.py')
#
def _import_module(module_name):
    """
    Return module object from file_path (.py) with module_name
    """
    import importlib.util

    filename = f"{module_name}.py"
    filepath = os.path.join(_THISDIR, filename)
    assert os.path.exists(filepath), f"'{filepath}' not found"

    spec = importlib.util.spec_from_file_location(module_name, filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module

# ------------------------------------------------------------------------


# Get the path *this* file is in:

# Import 'utils'
utils = _import_module("utils")

## Import Custom Spawner
custom_spawner = _import_module("custom_spawner")

# Get Jupyter default/built-in config
c = get_config()

# Spawn single-user servers as Docker containers
# c.JupyterHub.spawner_class = "dockerspawner.DockerSpawner"
c.JupyterHub.spawner_class = custom_spawner.CustomDockerSpawner

# c.DockerSpawner.image = os.environ["NOTEBOOK_DEFAULT_IMAGE"]
_images = utils.read_txt('imagelist')
if not _images:
    _images = [ 'jupyterhub/singleuser:latest' ]
c.DockerSpawner.images = _images

# JupyterHub requires a single-user instance of the Notebook server, so we
# default to using the `start-singleuser.sh` script included in the
# jupyter/docker-stacks *-notebook images as the Docker run command when
# spawning containers.  Optionally, you can override the Docker run command
# using the DOCKER_SPAWN_CMD environment variable.
c.DockerSpawner.cmd = os.environ["NOTEBOOK_SPAWN_CMD"]

# Connect containers to this Docker network
c.DockerSpawner.network_name = os.environ["DOCKER_NETWORK_NAME"]
c.DockerSpawner.use_internal_ip = True

# Explicitly set notebook directory because we'll be mounting a volume to it.
# Most jupyter/docker-stacks *-notebook images run the Notebook server as
# user `jovyan`, and set the notebook directory to `/home/jovyan/work`.
# We use, per default, jovyan's home directory (/home/jovyan) instead.
# If you want a different one, define notebook-dir in the environment.
notebook_dir = os.environ.get("NOTEBOOK_DIR", "/home/jovyan")
c.DockerSpawner.notebook_dir = notebook_dir


# ---
# Let's define the structure of folders we want users to have access
# ---

## Users' work dir/path
docker_work_dir = os.environ["NOTEBOOK_USERS_WORK_DIR"]
local_work_basedir = os.environ["HOST_USERS_WORK_BASEDIR"]
local_work_dir = local_work_basedir + "/{username}"

## Users' shared path
docker_shared_dir = os.environ["NOTEBOOK_USERS_SHARED_DIR"]
local_shared_dir = os.environ["HOST_USERS_SHARED_DIR"]

## Data path
docker_data_dir = os.environ["NOTEBOOK_DATA_DIR"]
local_data_dir = os.environ["HOST_DATA_DIR"]


## ISIS-Data path
docker_isisdata_dir = os.environ["NOTEBOOK_ISISDATA_DIR"]
local_isisdata_dir = os.environ["HOST_ISISDATA_DIR"]

c.DockerSpawner.volumes = {
    local_work_dir: docker_work_dir,
    local_data_dir: docker_data_dir,
    local_shared_dir: docker_shared_dir,
    local_isisdata_dir: docker_isisdata_dir,
}

# c.DockerSpawner.extra_create_kwargs = {'user': 'root'}
c.DockerSpawner.extra_create_kwargs.update({"user": "root"})

c.DockerSpawner.environment = {
    "CHOWN_HOME": "yes",
    "CHOWN_EXTRA": docker_work_dir,
    "CHOWN_HOME_OPTS": "-R",
    "NB_UID": 1000,
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


# ---
# User login/authentication interface
# ---

# If environment variable 'OAUTHENTICATOR' is defined, supposedly we are going
# to use 'Gitlab' or 'Github'. The variables used by either OAuth driver
# are provided in 'secrets/oauth.env'
#
if "OAUTHENTICATOR" in os.environ:

    if os.environ["OAUTHENTICATOR"].upper() == "GITLAB":
        from oauthenticator.gitlab import GitLabOAuthenticator

        c.JupyterHub.authenticator_class = GitLabOAuthenticator

    elif os.environ["OAUTHENTICATOR"].upper() == "GITHUB":
        from oauthenticator.github import GitHubOAuthenticator

        c.JupyterHub.authenticator_class = GitHubOAuthenticator

    else:
        print("Supported OAUTHENTICATOR values: 'GITLAB', 'GITHUB'")

else:
    # Authenticate users with Native Authenticator
    c.JupyterHub.authenticator_class = "nativeauthenticator.NativeAuthenticator"
    # Allow anyone to sign-up without approval
    c.NativeAuthenticator.open_signup = True


# ---
# Admin/Whitlelist users
# ---

whitelist = set()
admin = set()
try:
    with open(os.path.join(_THISDIR, "userlist"), "r") as f:
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

_admin = os.environ.get("JUPYTERHUB_ADMIN")
if _admin:
    admin.add(_admin)

c.JupyterHub.admin_access = True
c.Authenticator.admin_users = admin
c.Authenticator.allowed_users = whitelist

# ---
# Misc settings
# ---

# User’s default user interface to JupyterLab
c.Spawner.default_url = "/lab"

# Disable update notifications
c.LabApp.check_for_updates_class = "jupyterlab.NeverCheckForUpdate"
