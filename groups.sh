#!/bin/bash
source .env
NUM_GROUPS=4
for i in `seq 1 $NUM_GROUPS`; do
    docker volume create shared-$HUB_NAME-group$i
    sudo chmod 777 $(docker inspect shared-$HUB_NAME-group$i | grep "Mountpoint" | awk '{print $2}' | sed 's/"//g' | sed 's/,//g')
done

