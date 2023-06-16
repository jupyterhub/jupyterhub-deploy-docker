#!/usr/bin/env bash

# Additional things you want that might not be in the default shell:
# Home of Notebook user (/home/jovyan)
NB_HOME=$(getent passwd $NB_USER | cut -d':' -f6)

# Create link from User's home to data directory (from DATA_DIR env.variable)
[ ! "$DATA_DIR" == "" ] && ln -sfn $DATA_DIR $NB_HOME/data

DOCS="${NB_HOME}/docs"

mkdir -p $DOCS 2> /dev/null

README_FILE="${DOCS}/GMAP.md"
README_URL='https://raw.githubusercontent.com/europlanet-gmap/.github/main/profile/README.md'

if [ ! -f "$README_FILE" ];
then
  wget -q -O $README_FILE $README_URL
fi

jupyter labextension disable "@jupyterlab/apputils-extension:announcements"

# it should always end with this line, to start the notebook server:
# exec jupyterhub-singleuser "$@"
start-singleuser.sh
