#!/bin/bash
# Copyright (c) Jupyter Development Team.
# Distributed under the terms of the Modified BSD License.

# Wrapper script that runs https://letsencrypt.org Docker container to generate
# a certificate for a single domain and store it in a Docker volume.

set -e

USAGE="
Usage: `basename $0` --domain FQDN --email EMAIL --volume SECRETS_VOLUME
       [--staging]
"

while [[ $# > 0 ]]
do
key="$1"
case $key in
    --domain)
    FQDN="$2"
    shift # past argument
    ;;
    --email)
    EMAIL="$2"
    shift # past argument
    ;;
    --volume)
    SECRETS_VOLUME="$2"
    shift # past argument
    ;;
    --staging)
    CERT_SERVER=--staging
    ;;
    *) # unknown option
    ;;
esac
shift # past argument or value
done

if [ -z "${FQDN:+x}" ]; then
	echo "ERROR: Must provide --domain option or set FQDN environment varable"
  echo "$USAGE" && exit 1
fi

if [ -z "${EMAIL:+x}" ]; then
	echo "ERROR: Must provide --email option set EMAIL environment varable"
  echo "$USAGE" && exit 1
fi

if [ -z "${SECRETS_VOLUME:+x}" ]; then
  echo "ERROR: Must provide --volume option or set SECRETS_VOLUME environment varable"
  echo "$USAGE" && exit 1
fi

# letsencrypt certificate server type (default is production).
# Set `CERT_SERVER=--staging` for staging.
: ${CERT_SERVER=''}

# Generate the cert and save it to the Docker volume
docker run --rm -it \
  -p 80:80 \
  -v $SECRETS_VOLUME:/etc/letsencrypt \
  quay.io/letsencrypt/letsencrypt:latest \
  certonly \
  --non-interactive \
  --keep-until-expiring \
  --standalone \
  --standalone-supported-challenges http-01 \
  --agree-tos \
  --force-renewal \
  --domain "$FQDN" \
  --email "$EMAIL" \
  $CERT_SERVER

# Set permissions so nobody can read the cert and key.
# Also symlink the certs into the root of the /etc/letsencrypt
# directory so that the FQDN doesn't have to be known later.
docker run --rm -it \
  -v $SECRETS_VOLUME:/etc/letsencrypt \
  --entrypoint=/bin/bash \
  quay.io/letsencrypt/letsencrypt:latest \
  -c "find /etc/letsencrypt/* -maxdepth 1 -type l -delete && \
    ln -s /etc/letsencrypt/live/$FQDN/* /etc/letsencrypt/ && \
    find /etc/letsencrypt -type d -exec chmod 755 {} +"
