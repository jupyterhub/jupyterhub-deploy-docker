#!/usr/bin/env bash
set -ue

# This script prepare the environment for running the Hub.
# Preparation consists of:
# - Pull-or-build JupyterHub (server) image
# - Pull-or-build Notebook (client) images

HERE=$(pwd -P `dirname $BASH_SOURCE`)

function pull_notebook_images() {
    # Pull images from file './config/imageslist'
    FILE_IN="./config/imagelist"
    for image in `grep -E -v "^$|#" $FILE_IN`
    do
        echo "Getting image '$image'.."
        docker pull $image
        [ $? ] && echo "..done" || echo "..failed"
    done
}

function build_notebook_images() {
    # Build images from file './imageslist' overwrite file 'config/imageslist'
    # FILE_IN="${HERE}/imagelist"
    # DOCKERFILE="${HERE}/dockerfiles/singleuser.dockerfile"
    FILE_IN="./imagelist"
    DOCKERFILE="./dockerfiles/singleuser.dockerfile"
    CONTEXT=`dirname $DOCKERFILE`
    for src_image in `grep -E -v "^$|#" $FILE_IN`
    do
        dst_image="${src_image##*/}"
        echo "Building image '$dst_image' (from '$src_image').."
        docker build -t $dst_image --build-arg BASE_IMAGE="$src_image" \
                     -f $DOCKERFILE $CONTEXT
        [ $? ] && echo "..done" || echo "..failed"
    done
}

function build_jupyterhub_image() {
    # Build jupyterhub image
    # DOCKERFILE="${HERE}/dockerfiles/jupyterhub.dockerfile"
    # CONTEXT=`dirname $DOCKERFILE`
    # dst_image="jupyterhub"
    # echo "Building '$dst_image' image.."
    # docker build -t $dst_image -f $DOCKERFILE $CONTEXT
    # [ $? ] && echo "..done" || echo "..failed"
    docker compose -f compose.build.yml build jupyterhub
}


#!/bin/bash

# Default values
PULL_NOTEBOOK_IMAGES=false
BUILD_NOTEBOOK_IMAGES=false
BUILD_JUPYTERHUB_IMAGE=false
QUIET=false

# Function to display script usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  -p, --pull_notebook_images   Pull notebook images"
    echo "  -b, --build_notebook_images  Build notebook images"
    echo "  -j, --build_jupyterhub_image Build JupyterHub image"
    echo "  -q, --quiet                  Suppress output from docker"
    echo "  -h, --help                   Display this help message"
    exit 1
}

# If no options are provided, display usage
if [[ "$#" -eq 0 ]]; then
    usage
fi

# Parse command line options
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--pull_notebook_images)
            PULL_NOTEBOOK_IMAGES=true
            ;;
        -b|--build_notebook_images)
            BUILD_NOTEBOOK_IMAGES=true
            ;;
        -j|--build_jupyterhub_image)
            BUILD_JUPYTERHUB_IMAGE=true
            ;;
        -q|--quiet)
            QUIET=true
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Invalid option: $1"
            usage
            ;;
    esac
    shift
done

# Perform actions based on options
if $PULL_NOTEBOOK_IMAGES; then
    echo "Pulling notebook images..."
    pull_notebook_images
fi

if $BUILD_NOTEBOOK_IMAGES; then
    echo "Building notebook images..."
    build_notebook_images
fi

if $BUILD_JUPYTERHUB_IMAGE; then
    echo "Building JupyterHub image..."
    build_jupyterhub_image
fi
