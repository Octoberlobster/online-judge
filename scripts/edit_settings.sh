#!/usr/bin/env bash
set -euo pipefail


# Configuration values
SECRET_KEY=''                                            # Django 密鑰（格式：字串，建議 50+ 字元）
ALLOWED_HOSTS=''                                         # 允許的主機（格式：IP/域名，逗號分隔）
DB_USER=''                                               # 資料庫使用者名稱（格式：字串）
DB_PASSWORD=''                                           # 資料庫密碼（格式：字串）
STATIC_ROOT=''                                           # Django 靜態檔案收集路徑（專案絕對路徑）
BRIDGE_JUDGE=''                                          # Judge 橋接地址（格式：IP:Port，逗號分隔多個）
BRIDGE_DJANGO=''                                         # Django 橋接地址（格式：IP:Port，逗號分隔多個）
EMAIL_HOST_USER=''                                       # 郵件伺服器使用者（格式：電子郵件地址）
EMAIL_HOST_PASSWORD=''                                   # 郵件伺服器密碼（格式：字串或應用程式專用密碼）
CONFIG_FILE=""                                # uwsgi 設定檔路徑（相對於目前目錄）
NEW_CHDIR=""                           # uwsgi 工作目錄路徑（專案根目錄絕對路徑）
NEW_PYTHONPATH=""                      # Python 模組搜尋路徑（專案根目錄絕對路徑）
NEW_VIRTUALENV=""                       # Python 虛擬環境路徑（虛擬環境根目錄絕對路徑）
# uwsgi.ini 檔案的絕對路徑
UWSGI_INI_PATH=""
# 專案根目錄的絕對路徑
PROJECT_DIRECTORY=""
# bridged 服務的執行指令路徑
BRIDGE_COMMAND_PATH=""
# 專案的 Python 路徑
PYTHON_PATH=""
# celery 服務的執行指令路徑
CELERY_COMMAND_PATH=""
# celery 服務的使用者和群組
CELERY_USER=""
CELERY_GROUP=""
# websocket 服務的執行指令路徑
EVENT_COMMAND_PATH=""
# websocket 服務的 Node.js 模組路徑
NODE_PATH=""
# websocket 服務的使用者和群組
EVENT_USER=""
EVENT_GROUP=""
PORT=                          # 例：80 或 12080
SERVER_NAME=""            # 只填主機名，不要含 http:// 或 https://
ROOT_DIR=""       # 用於 502.html / logo.png / robots.txt 及 icons
STATIC_ALIAS=""  # /static 對應的實際路徑（結尾建議保留 /）
CONF_PATH=""    # 產生的 nginx 設定檔路徑

. "${NEW_VIRTUALENV}/bin/activate"
# prevent recursion
if [ "${EDIT_SETTINGS_RUNNING:-}" = "true" ]; then
    echo "Script already running, preventing recursion" >&2
    exit 1
fi
export EDIT_SETTINGS_RUNNING=true

echo "updating local_settings.py..."

cd dmoj

# check local_settings.py exist
if [ ! -f "local_settings.py" ]; then
    echo "錯誤: local_settings.py 檔案不存在於當前目錄" >&2
    exit 1
fi

# backup local_settings.py
cp local_settings.py local_settings.py.backup
echo "backup finished local_settings.py.backup"

# use sed to modify setting
echo "updating SECRET_KEY..."
sed -i "s/SECRET_KEY = ''/SECRET_KEY = '$SECRET_KEY'/" local_settings.py

echo "updating ALLOWED_HOSTS..."
sed -i "s/ALLOWED_HOSTS = \['127.0.0.1','0.0.0.0','localhost'\]/ALLOWED_HOSTS = ['$(echo $ALLOWED_HOSTS | sed "s/,/', '/g")']/" local_settings.py

echo "updating database setting..."
sed -i "s/'USER': 'User Name',/'USER': '$DB_USER',/" local_settings.py
sed -i "s/'PASSWORD': 'User Password',/'PASSWORD': '$DB_PASSWORD',/" local_settings.py

echo "updating STATIC_ROOT..."
sed -i "s|STATIC_ROOT = '/static'|STATIC_ROOT = '$STATIC_ROOT'|" local_settings.py

echo "updating Bridge setting..."

BRIDGE_JUDGE_FORMATTED=""
IFS=',' read -ra JUDGE_ADDRS <<< "$BRIDGE_JUDGE"
for addr in "${JUDGE_ADDRS[@]}"; do
    IFS=':' read -ra PARTS <<< "$addr"
    IP="${PARTS[0]}"
    PORT="${PARTS[1]}"
    if [ -n "$BRIDGE_JUDGE_FORMATTED" ]; then
        BRIDGE_JUDGE_FORMATTED="$BRIDGE_JUDGE_FORMATTED, "
    fi
    BRIDGE_JUDGE_FORMATTED="$BRIDGE_JUDGE_FORMATTED('$IP', $PORT)"
done

sed -i "s/BRIDGED_JUDGE_ADDRESS = \[('localhost', 8098)\]/BRIDGED_JUDGE_ADDRESS = [$BRIDGE_JUDGE_FORMATTED]/" local_settings.py

BRIDGE_DJANGO_FORMATTED=""
IFS=',' read -ra DJANGO_ADDRS <<< "$BRIDGE_DJANGO"
for addr in "${DJANGO_ADDRS[@]}"; do
    IFS=':' read -ra PARTS <<< "$addr"
    IP="${PARTS[0]}"
    PORT="${PARTS[1]}"
    if [ -n "$BRIDGE_DJANGO_FORMATTED" ]; then
        BRIDGE_DJANGO_FORMATTED="$BRIDGE_DJANGO_FORMATTED, "
    fi
    BRIDGE_DJANGO_FORMATTED="$BRIDGE_DJANGO_FORMATTED('$IP', $PORT)"
done

sed -i "s/BRIDGED_DJANGO_ADDRESS = \[('localhost', 8099)\]/BRIDGED_DJANGO_ADDRESS = [$BRIDGE_DJANGO_FORMATTED]/" local_settings.py

echo "updating Email setting..."
sed -i "s/EMAIL_HOST_USER = ''/EMAIL_HOST_USER = '$EMAIL_HOST_USER'/" local_settings.py
sed -i "s/EMAIL_HOST_PASSWORD = ''/EMAIL_HOST_PASSWORD = '$EMAIL_HOST_PASSWORD'/" local_settings.py

echo "Configuration Done"
echo ""
echo "已更新的設定值："
echo "- SECRET_KEY: $SECRET_KEY"
echo "- ALLOWED_HOSTS: $ALLOWED_HOSTS"
echo "- DB_USER: $DB_USER"  
echo "- DB_PASSWORD: [已設定]"
echo "- STATIC_ROOT: $STATIC_ROOT"
echo "- BRIDGE_JUDGE: $BRIDGE_JUDGE_FORMATTED"
echo "- BRIDGE_DJANGO: $BRIDGE_DJANGO_FORMATTED"
echo "- EMAIL_HOST_USER: $EMAIL_HOST_USER"
echo "- EMAIL_HOST_PASSWORD: [已設定]"
echo ""
echo "原始檔案已備份至 local_settings.py.backup"
cd ../
python3 manage.py check

#---------------step6--------------
./make_style.sh
python3 manage.py collectstatic --noinput
python3 manage.py compilemessages
python3 manage.py compilejsi18n
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py loaddata navbar
python3 manage.py loaddata language_all
python3 manage.py loaddata demo
python3 manage.py createsuperuser

#install uwsgi
pip3 install uwsgi
if [ ! -f "$CONFIG_FILE" ]; then
    echo "錯誤：找不到 $CONFIG_FILE 檔案！"
    exit 1
fi

echo "---"
echo "正在修改 uwsgi.ini 檔案..."
echo "---"

# modify chdir
if [ -n "$NEW_CHDIR" ]; then
    sed -i "s|^chdir =.*|chdir = $NEW_CHDIR|" "$CONFIG_FILE"
    echo "chdir 已更新為：$NEW_CHDIR"
fi

# modify pythonpath
if [ -n "$NEW_PYTHONPATH" ]; then
    sed -i "s|^pythonpath =.*|pythonpath = $NEW_PYTHONPATH|" "$CONFIG_FILE"
    echo "pythonpath 已更新為：$NEW_PYTHONPATH"
fi

# modify virtualenv
if [ -n "$NEW_VIRTUALENV" ]; then
    sed -i "s|^virtualenv =.*|virtualenv = $NEW_VIRTUALENV|" "$CONFIG_FILE"
    echo "virtualenv 已更新為：$NEW_VIRTUALENV"
fi

echo "---"
echo "uwsgi.ini 檔案修改完成！"

#edit_supervisor conf
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

#setup nginx
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

unset EDIT_SETTINGS_RUNNING

