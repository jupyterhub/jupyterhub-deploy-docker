#!/bin/bash

# load environmental variables into the bash session's namespace
source .env
source secrets/oauth.env
# run ephemeral docker container to print out password.
echo "Password for username: hub-admin is "
docker run --rm $HUB_NAME hashauthpw --length $PASSWORD_LENGTH hub-admin $HASH_SECRET_KEY

echo "Password for username: $USERNAME is "
docker run --rm $HUB_NAME hashauthpw --length $PASSWORD_LENGTH $USERNAME $HASH_SECRET_KEY

