#!/bin/bash

# User should be set to root in the docker file before calling this.

set -e
set -x

userdel student

# Home dir has been mounted by jupyterhub as a docker volume
shopt -s dotglob
for i in /home/student/*; do ln -sf $i /home/${NB_USER}; done
shopt -u dotglob

NB_UID=40000
NB_GID=40000
NB_GROUP=student

# User home directory will already exist because DockerSpawner mounted a docker volume at /home/$NB_USER
groupadd -g ${NB_GID} ${NB_GROUP}
useradd -u ${NB_UID} ${NB_USER} --gid ${NB_GROUP}

cd /home/${NB_USER}
###################################################################################


########################## Set up directories #####################################
# Create directory for notebooks.

mkdir -p /home/${NB_USER}/${NOTEBOOK_DIR}
#mkdir -p /home/${NB_USER}/.jupyter

chmod 600 /tmp/students.csv
chown ${INSTRUCTOR_UID}:${INSTRUCTOR_GID} /tmp/students.csv

chown ${INSTRUCTOR_UID}:${INSTRUCTOR_GID} /srv/nbgrader/${COURSE_NAME}
echo ${NBGRADER_DB_URL} > /srv/nbgrader/${COURSE_NAME}/nbgrader_db.url
unset NBGRADER_DB_URL

# Make exchange directory readable and writable by everyone.
# Take exchange directory as environment variable later.
# This should be same volume mounted on each user's docker container.
chmod 777 /srv/nbgrader/exchange
chown ${INSTRUCTOR_UID}:${INSTRUCTOR_GID} /srv/nbgrader/exchange

chown -R ${NB_USER}:${NB_GROUP} /home/${NB_USER}


################## Disable extensions for students #############################
jupyter nbextension enable nbgrader --user --py
jupyter serverextension enable nbgrader --user --py
jupyter nbextension disable --user create_assignment/main
jupyter nbextension disable --user formgrader/main --section=tree
jupyter nbextension disable --user course_list/main --section=tree
jupyter serverextension disable --user nbgrader.server_extensions.formgrader

################################################################################


# Start the single user notebook.
exec /home/${NB_USER}/.local/bin/start-singleuser-custom.sh $*
