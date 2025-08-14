#!/usr/bin/env bash
set -euo pipefail

# 防止遞迴保護
if [ "${EDIT_SETTINGS_RUNNING:-}" = "true" ]; then
    echo "Script already running, preventing recursion" >&2
    exit 1
fi
export EDIT_SETTINGS_RUNNING=true

# Configuration values - 填入你的真實數值
SECRET_KEY='thisiskey'
ALLOWED_HOSTS='example.com,127.0.0.1,localhost'
DB_USER='xc'
DB_PASSWORD='Mbuibm9290'
STATIC_ROOT='/test/www/dmoj/static'
BRIDGE_JUDGE='1.2.3.4:7779,0.0.0.0:8888'
BRIDGE_DJANGO='127.0.0.1:9988'
EMAIL_HOST_USER='noreply@example.com'
EMAIL_HOST_PASSWORD='trgsuhakhtgzhrtd'

echo "正在更新 local_settings.py..."

cd dmoj

# 檢查 local_settings.py 是否存在
if [ ! -f "local_settings.py" ]; then
    echo "錯誤: local_settings.py 檔案不存在於當前目錄" >&2
    exit 1
fi

# 備份原始檔案
cp local_settings.py local_settings.py.backup
echo "已備份原始檔案至 local_settings.py.backup"

# 使用 sed 修改各個設定值
echo "更新 SECRET_KEY..."
sed -i "s/SECRET_KEY = ''/SECRET_KEY = '$SECRET_KEY'/" local_settings.py

echo "更新 ALLOWED_HOSTS..."
sed -i "s/ALLOWED_HOSTS = \['127.0.0.1','0.0.0.0','localhost'\]/ALLOWED_HOSTS = ['$(echo $ALLOWED_HOSTS | sed "s/,/', '/g")']/" local_settings.py

echo "更新資料庫設定..."
sed -i "s/'USER': 'User Name',/'USER': '$DB_USER',/" local_settings.py
sed -i "s/'PASSWORD': 'User Password',/'PASSWORD': '$DB_PASSWORD',/" local_settings.py

echo "更新 STATIC_ROOT..."
sed -i "s|STATIC_ROOT = '/static'|STATIC_ROOT = '$STATIC_ROOT'|" local_settings.py

echo "更新 Bridge 設定..."
# 處理 BRIDGED_JUDGE_ADDRESS - 將 IP:PORT 格式轉換為 ('IP', PORT) 格式
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

# 處理 BRIDGED_DJANGO_ADDRESS - 將 IP:PORT 格式轉換為 ('IP', PORT) 格式
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

echo "更新 Email 設定..."
sed -i "s/EMAIL_HOST_USER = ''/EMAIL_HOST_USER = '$EMAIL_HOST_USER'/" local_settings.py
sed -i "s/EMAIL_HOST_PASSWORD = ''/EMAIL_HOST_PASSWORD = '$EMAIL_HOST_PASSWORD'/" local_settings.py

echo "配置完成！"
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
# 編譯 SCSS / PostCSS 樣式
./make_style.sh
# 收集所有靜態資源到您在 local_settings.py 設定的 STATIC_ROOT
python3 manage.py collectstatic --noinput
# 生成 internationalization files
python3 manage.py compilemessages
python3 manage.py compilejsi18n
python3 manage.py makemigrations
python3 manage.py migrate

#載入初始資料
python3 manage.py loaddata navbar
python3 manage.py loaddata language_all

#建立管理員資料
python3 manage.py createsuperuser

unset EDIT_SETTINGS_RUNNING
 