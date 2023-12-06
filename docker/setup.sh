#!/usr/bin/env bash
set -ue

# This script prepare the environment for running the Hub.
# Preparation consists of:
# - Pull-or-build JupyterHub (server) image
# - Pull-or-build Notebook (client) images

HERE=$(pwd -P `dirname $BASH_SOURCE`)

function pull_notebook_images() {
    # Pull images from file './config/imageslist'
    FILE_IN="${HERE}/config/imagelist"
    for image in `grep -E -v "^$|#" $FILE_IN`
    do 
        echo "Getting image $image .."
        docker pull -q $image
        [ $? ] && echo "..done" || echo "..failed"
    done
}

function build_notebook_images() {
    # Build images from file './imageslist' overwrite file 'config/imageslist'
    FILE_IN="${HERE}/imagelist"
    DOCKERFILE="${HERE}/dockerfiles/singleuser.dockerfile"
    CONTEXT=`dirname $DOCKERFILE`
    for src_image in `grep -E -v "^$|#" $FILE_IN`
    do 
        dst_image="${src_image##*/}"
        echo "Building image $dst_image (from $src_image) .."
        docker build -q -t $dst_image --build-arg BASE_IMAGE="$src_image" -f $DOCKERFILE $CONTEXT
        [ $? ] && echo "..done" || echo "..failed"
    done
}

function build_jupyterhub_image() {
    # Build jupyterhub image
    DOCKERFILE="${HERE}/dockerfiles/jupyterhub.dockerfile"
    CONTEXT=`dirname $DOCKERFILE`
    dst_image="jupyterhub"
    echo "Building $dst_image image .."
    docker build -q -t $dst_image -f $DOCKERFILE $CONTEXT
    [ $? ] && echo "..done" || echo "..failed"

}

# pull_notebook_images
# build_notebook_images
build_jupyterhub_image
