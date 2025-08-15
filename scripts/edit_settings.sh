#!/usr/bin/env bash
set -euo pipefail


SECRET_KEY='thisiskey'
ALLOWED_HOSTS='0.0.0.0,127.0.0.1,localhost'
DB_USER='DB_USER'
DB_PASSWORD='DB_PASSWORD'
STATIC_ROOT='path to/dmoj-site/static'
BRIDGE_JUDGE='localhost:8098'
BRIDGE_DJANGO='localhost:8099'
EMAIL_HOST_USER='EMAIL_HOST_USER'
EMAIL_HOST_PASSWORD='EMAIL_HOST_PASSWORD'
CONFIG_FILE="./uwsgi.ini"
NEW_CHDIR="path to/dmoj-site"
NEW_PYTHONPATH="path to/dmoj-site"
NEW_VIRTUALENV="path to/dmojsite"
# uwsgi.ini 檔案的絕對路徑
UWSGI_INI_PATH="path to/dmojsite/bin/uwsgi --ini uwsgi.ini"


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


