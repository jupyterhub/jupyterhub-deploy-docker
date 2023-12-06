#!/usr/bin/env bash
set -e

# This script prepare the environment for running the Hub.
# Preparation consists of:
# - Pull-or-build JupyterHub (server) image
# - Pull-or-build Notebook (client) images

HERE=$(pwd -P `dirname $BASH_SOURCE`)

function pull_notebook_images() {
    # Pull images from file './config/imageslist'
    FILE_IN="${HERE}/config/imageslist"
    for image in `grep -E -v "^$|#" $FILE_IN`
    do 
        # echo "Getting image $image .."
        docker pull -q $image
        # [ $? ] && echo "..done" || echo "..failed"
    done
}

# function build_notebook_images() {
#     # Build images from file './imageslist' overwrite file 'config/imageslist'
#     FILE_IN="${HERE}/imageslist"
# }

pull_notebook_images