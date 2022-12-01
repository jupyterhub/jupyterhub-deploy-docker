#!/bin/sh
set -eu

count=0
started=0
# Max 5 minutes
while [ $count -lt 60 ]; do
    sleep 5
    if curl -s http://localhost:8000/hub/api/; then
        started=1
        break
    fi
    echo -n .
    count=$((count+1))
done
if [ $started -eq 0 ]; then
    echo "*****"
    echo "JupyterHub did not start"
    echo "*****"
    docker-compose logs
    exit 1
fi
