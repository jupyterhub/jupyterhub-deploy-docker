#!/bin/bash
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# Wrapper script around docker-compose

set -e

for i in "$@" ; do
  if [[ "$i" == "up" ]]; then
    # Check for required environment variables on startup
    if [ -z ${GITHUB_CLIENT_ID:+x} ]; then
      echo "ERROR: Must set GITHUB_CLIENT_ID environment variable"; exit 1;
    fi
    if [ -z ${GITHUB_CLIENT_SECRET:+x} ]; then
      echo "ERROR: Must set GITHUB_CLIENT_SECRET environment variable"; exit 1;
    fi
    if [ -z ${OAUTH_CALLBACK_URL:+x} ]; then
      echo "ERROR: Must set OAUTH_CALLBACK_URL environment variable"; exit 1;
    fi
  fi
done

exec docker-compose "$@"
