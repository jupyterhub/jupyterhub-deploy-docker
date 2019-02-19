#!/bin/bash

# this script is meant to be run only the first time a hub is being set up.

# create a default userlist
echo "Use the format \"studentname HUB_NAME-group1\" on each line to add students to groups (10 by default have already been created and permissions appropriately set)" > userlist
echo "hub-admin admin shared" >> userlist

# change permissions so that admins can edit these.
sudo chmod 777 userlist
sudo chmod 777 jupyterhub_config.py

mkdir secrets
make secrets/oauth.env
make secrets/postgres.env
echo "HUB_LOC=$(pwd)" >> .env

source .env
# show what is needed to be added to /etc/nginx/sites-enabled/hub.conf

echo -en "\nBuilding Hub $HUB_NAME. Please be patient. This may take up to 15 minutes, depending on your hardware."
make notebook_image
make build
docker-compose up -d

echo -en "\n\nWe create a default shared volume and set its permissions to be read/write. You may have to enter your password now:\n"
docker volume create shared-shared
sudo chmod 777 $(docker inspect shared-shared | grep "Mountpoint" | awk '{print $2}' | sed 's/"//g' | sed 's/,//g')
echo -en "Globally shared volume has been created."

echo -en "\n\nHub has been launched. Here are the Docker processes running right now:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"


echo -en "\n\nCONGRATS!!! Hub $HUB_NAME has been created and launched!. Please add the following to /etc/nginx/sites-enabled/hub.conf. Run\n"
echo -en "\n\tsudo vim /etc/nginx/sites-enabled/hub.conf \n\nand enter the following into the server entry:\n"
echo -en "\nlocation /$HUB_NAME { \n\t proxy_pass http://127.0.0.1:$PORT_NUM; \n\t proxy_set_header X-Real-IP \$remote_addr; \n\t proxy_set_header Host \$host; \n\t proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for; \n\t # websocket headers \n\t proxy_set_header Upgrade \$http_upgrade; \n\t proxy_set_header Connection \$connection_upgrade; \n } \n\n"

echo -en "After you add that and restart nginx with \n\tsudo service nginx restart\nyou can access your hub using\n\n"
bash show_login.sh
