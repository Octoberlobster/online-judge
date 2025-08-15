#!/bin/bash

# =================================================================
# 請在這裡填入你專案的實際路徑
# =================================================================
# uwsgi.ini 檔案的絕對路徑
UWSGI_INI_PATH="${HOME}/dmojsite/bin/uwsgi --ini uwsgi.ini"
# 專案根目錄的絕對路徑
PROJECT_DIRECTORY="${HOME}/dmoj-site"
# bridged 服務的執行指令路徑
BRIDGE_COMMAND_PATH="${HOME}/dmojsite/bin/python manage.py runbridged"
# 專案的 Python 路徑
PYTHON_PATH="${HOME}/dmoj-site"
# celery 服務的執行指令路徑
CELERY_COMMAND_PATH="${HOME}/dmojsite/bin/celery -A dmoj_celery worker"
# celery 服務的使用者和群組
CELERY_USER="aiversity0"
CELERY_GROUP="aiversity0"
# websocket 服務的執行指令路徑
EVENT_COMMAND_PATH="${HOME}/dmoj-site/websocket/daemon.js"
# websocket 服務的 Node.js 模組路徑
NODE_PATH="${HOME}/dmoj-site/websocket/node_modules"
# websocket 服務的使用者和群組
EVENT_USER="aiversity0"
EVENT_GROUP="aiversity0"
# =================================================================

# 檢查變數是否已填寫
if [ -z "$UWSGI_INI_PATH" ] || [ -z "$PROJECT_DIRECTORY" ] || [ -z "$BRIDGE_COMMAND_PATH" ] || [ -z "$PYTHON_PATH" ] || [ -z "$CELERY_COMMAND_PATH" ] || [ -z "$CELERY_USER" ] || [ -z "$CELERY_GROUP" ] || [ -z "$EVENT_COMMAND_PATH" ] || [ -z "$NODE_PATH" ] || [ -z "$EVENT_USER" ] || [ -z "$EVENT_GROUP" ]; then
    echo "錯誤：請先在腳本中填寫所有必要的路徑變數！"
    exit 1
fi

echo "---"
echo "正在開始設定 Supervisor..."
echo "---"

# 1. 安裝 supervisor
echo "正在安裝 supervisor..."
apt update && apt install -y supervisor

# 2. 建立 site.conf 設定檔
SITE_CONF_FILE="/etc/supervisor/conf.d/site.conf"
echo "正在建立 $SITE_CONF_FILE..."
cat <<EOF > "$SITE_CONF_FILE"
[program:site]
command=$UWSGI_INI_PATH
directory=$PROJECT_DIRECTORY
stopsignal=QUIT
stdout_logfile=/tmp/site.stdout.log
stderr_logfile=/tmp/site.stderr.log
EOF

# 3. 建立 bridged.conf 設定檔
BRIDGE_CONF_FILE="/etc/supervisor/conf.d/bridged.conf"
echo "正在建立 $BRIDGE_CONF_FILE..."
cat <<EOF > "$BRIDGE_CONF_FILE"
[program:bridged]
command=$BRIDGE_COMMAND_PATH
directory=$PROJECT_DIRECTORY
environment=DJANGO_SETTINGS_MODULE="dmoj.settings",PYTHONPATH="$PYTHON_PATH"
stopsignal=INT
user=root
group=root
stdout_logfile=/tmp/bridge.stdout.log
stderr_logfile=/tmp/bridge.stderr.log
EOF

# 4. 建立 celery.conf 設定檔
CELERY_CONF_FILE="/etc/supervisor/conf.d/celery.conf"
echo "正在建立 $CELERY_CONF_FILE..."
cat <<EOF > "$CELERY_CONF_FILE"
[program:celery]
command=$CELERY_COMMAND_PATH
directory=$PROJECT_DIRECTORY
user=$CELERY_USER
group=$CELERY_GROUP
stdout_logfile=/tmp/celery.stdout.log
stderr_logfile=/tmp/celery.stderr.log
EOF

# 5. 建立 EVENT.conf 設定檔
EVENT_CONF_FILE="/etc/supervisor/conf.d/event.conf"
echo "正在建立 $EVENT_CONF_FILE..."
cat <<EOF > "$EVENT_CONF_FILE"
[program:event]
command=/usr/bin/node $EVENT_COMMAND_PATH
environment=NODE_PATH="$NODE_PATH"
user=$EVENT_USER
group=$EVENT_GROUP
stdout_logfile=/tmp/event.stdout.log
stderr_logfile=/tmp/event.stderr.log
EOF

# 檢查檔案是否建立成功
if [ $? -ne 0 ]; then
    echo "錯誤：無法建立設定檔。請檢查權限或路徑。"
    exit 1
fi

# 6. 重新載入並更新 supervisor
echo "正在重新載入 supervisor 設定..."
supervisorctl reread
supervisorctl update
supervisorctl start all

echo "---"
echo "Supervisor 設定完成！"
echo "你可以使用 'sudo supervisorctl status' 來檢查所有服務的狀態。"

#!/usr/bin/env bash
set -Eeuo pipefail

### ===== 使用者可調整區 =====
PORT=12080                           # 例：80 或 12080
SERVER_NAME="IP"            # 只填主機名，不要含 http:// 或 https://
ROOT_DIR="${HOME}/dmoj-site"       # 用於 502.html / logo.png / robots.txt 及 icons
STATIC_ALIAS="${HOME}/dmoj-site/static/"  # /static 對應的實際路徑（結尾建議保留 /）
CONF_PATH="/etc/nginx/conf.d/nginx.conf"    # 產生的 nginx 設定檔路徑
### ===== 可調整區結束 =====

# 需要 root 寫入 /etc
if [[ ${EUID:-$(id -u)} -ne 0 ]]; then
  echo "請用 sudo 執行：sudo bash $0"
  exit 1
fi

# 簡單清理 server_name（避免誤填協定/尾斜線）
SANITIZED_SERVER_NAME="${SERVER_NAME#http://}"
SANITIZED_SERVER_NAME="${SANITIZED_SERVER_NAME#https://}"
SANITIZED_SERVER_NAME="${SANITIZED_SERVER_NAME%/}"

tee "$CONF_PATH" >/dev/null <<EOF
server {
    listen       ${PORT};
    listen       [::]:${PORT};

    # Change port to 443 and do the nginx ssl stuff if you want it.

    # Change server name to the HTTP hostname you are using.
    # You may also make this the default server by listening with default_server,
    # if you disable the default nginx server declared.
    server_name ${SANITIZED_SERVER_NAME};

    add_header X-UA-Compatible "IE=Edge,chrome=1";
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    charset utf-8;
    try_files \$uri @icons;
    error_page 502 504 /502.html;

    location ~ ^/502\\.html$|^/logo\\.png$|^/robots\\.txt$ {
        root ${ROOT_DIR};
    }

    location @icons {
        root ${ROOT_DIR}/resources/icons;
        error_page 403 = @uwsgi;
        error_page 404 = @uwsgi;
    }

    location @uwsgi {
        uwsgi_read_timeout 600;
        # Change this path if you did so in uwsgi.ini
        uwsgi_pass unix:///tmp/dmoj-site.sock;
        include uwsgi_params;
        uwsgi_param SERVER_SOFTWARE nginx/\$nginx_version;
    }

    location /static {
        gzip_static on;
        expires max;
        #root <django setting STATIC_ROOT, without the final /static>;
        # Comment out root, and use the following if it doesn't end in /static.
        alias ${STATIC_ALIAS};
    }

    # Uncomment these sections if you are using the event server.
    location /event/ {
        proxy_pass http://127.0.0.1:15100/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }

    location /channels/ {
        proxy_read_timeout          120;
        proxy_pass http://127.0.0.1:15102;
    }
}
EOF

sudo nginx -t && sudo systemctl reload nginx && echo "已寫入 ${CONF_PATH}（語法 OK）。/"

#!/bin/bash
DMOJ_STATIC_PATH="${HOME}/dmoj-site/static"
sudo apt update
sudo apt install -y acl
sudo setfacl -m u:www-data:x /home
sudo setfacl -m u:www-data:x "${HOME}"
sudo setfacl -R -m u:www-data:rx "$DMOJ_STATIC_PATH"
sudo setfacl -R -m d:u:www-data:rx "$DMOJ_STATIC_PATH"