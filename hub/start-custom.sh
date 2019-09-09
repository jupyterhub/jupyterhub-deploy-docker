#!/bin/bash

# User should be set to root in the docker file before calling this.

set -e
set -x

# Don't delete the contents of opam's home directory!
userdel opam

shopt -s dotglob
for i in /home/opam/*; do ln -sf $i /home/${NB_USER}; done
shopt -u dotglob
ln -sf /home/${NB_USER} /home/opam

############################ Create user and group ################################
# Add user and group.
if id "${NB_USER}" >/dev/null 2>&1; then
        echo "User ${NB_USER} exists."
else
	echo "User does not exist. Adding user ${NB_USER} (${NB_UID})"
	# User home directory will already exist because DockerSpawner mounted a docker volume at /home/$NB_USER
	useradd -u ${NB_UID} ${NB_USER}
fi

if getent group ${NB_GROUP} > /dev/null 2>&1; then
        echo "Group ${NB_GROUP} exists."
else
	echo "Group does not exist. Adding group ${NB_GROUP} (${NB_GID})"
	groupadd -g ${NB_GID} ${NB_GROUP}
fi

# Change group id of the group. Following line is a no op if group $NB_GROUP already has gid $NB_GID
groupmod -g ${NB_GID} ${NB_GROUP}
# Change id and group of the user. Following line is a no op if there is no change.
usermod -u ${NB_UID} -g ${NB_GID} ${NB_USER}
cd /home/${NB_USER}
###################################################################################



########################## Set up directories #####################################
# Create directory for notebooks.
mkdir -p /home/${NB_USER}/${NOTEBOOK_DIR}
#mkdir -p /home/${NB_USER}/.jupyter

chmod 600 /tmp/students.csv
chown ${INSTRUCTOR_UID}:${INSTRUCTOR_GID} /tmp/students.csv

chown ${INSTRUCTOR_UID}:${INSTRUCTOR_GID} /srv/nbgrader/${COURSE_NAME}

# Make exchange directory readable and writable by everyone.
# Take exchange directory as environment variable later.
# This should be same volume mounted on each user's docker container.
chmod 777 /srv/nbgrader/exchange
chown ${INSTRUCTOR_UID}:${INSTRUCTOR_GID} /srv/nbgrader/exchange

if [[ "${IS_INSTRUCTOR}" == "true" && ! -L "/home/$NB_USER/${NOTEBOOK_DIR}/${COURSE_NAME}" ]] ; then
  # If the user is instructor then point to course directory from user's home.
  ln -sf /srv/nbgrader/${COURSE_NAME} /home/$NB_USER/${NOTEBOOK_DIR}/${COURSE_NAME} 
fi

chown -R ${NB_USER}:${NB_GROUP} /home/${NB_USER}
##################################################################################

export PATH=$PATH:/home/${NB_USER}/.local/bin
# Import students.
if [[ "${IS_INSTRUCTOR}" == "true" ]] ; then
  # If the user is instructor, then import students in nbgrader database.
  su $NB_USER -c "env PATH=$PATH nbgrader db student import /tmp/students.csv"
fi

################## Disable extensions for students #############################
if [[ "${IS_INSTRUCTOR}" != "true" ]] ; then
  jupyter nbextension disable --sys-prefix create_assignment/main
  jupyter nbextension disable --sys-prefix formgrader/main --section=tree
  jupyter serverextension disable --sys-prefix nbgrader.server_extensions.formgrader
fi
################################################################################


# Start the single user notebook.
exec /home/${NB_USER}/.local/bin/start-singleuser-custom.sh $*
