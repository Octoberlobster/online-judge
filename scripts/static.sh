#!/bin/bash
DMOJ_STATIC_PATH="${HOME}/dmoj-site/static"
sudo apt update
sudo apt install -y acl
sudo setfacl -m u:www-data:x /home
sudo setfacl -m u:www-data:x "${HOME}"
sudo setfacl -R -m u:www-data:rx "$DMOJ_STATIC_PATH"
sudo setfacl -R -m d:u:www-data:rx "$DMOJ_STATIC_PATH"