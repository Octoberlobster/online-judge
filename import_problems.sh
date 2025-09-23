#!/bin/bash
# DMOJ 題目資料匯入腳本
# 使用方法：./import_problems.sh [資料庫名稱] [使用者名稱] [主機] [埠號]

# 設定預設值
DB_NAME=${1:-dmoj}
DB_USER=${2:-dmoj}
DB_HOST=${3:-localhost}
DB_PORT=${4:-3306}

SQL_FILE="dmoj_problems_export.sql"

echo "=== DMOJ 題目資料匯入 ==="
echo "資料庫名稱: $DB_NAME"
echo "使用者名稱: $DB_USER"
echo "主機地址: $DB_HOST"
echo "埠號: $DB_PORT"
echo "SQL 檔案: $SQL_FILE"
echo

# 檢查 SQL 檔案是否存在
if [ ! -f "$SQL_FILE" ]; then
    echo "錯誤: 找不到 SQL 檔案 '$SQL_FILE'"
    echo "請確保檔案在當前目錄中"
    exit 1
fi

# 顯示檔案資訊
echo "SQL 檔案大小: $(du -h $SQL_FILE | cut -f1)"
echo "SQL 檔案行數: $(wc -l < $SQL_FILE)"
echo

# 確認匯入
read -p "確定要匯入嗎？(y/N): " confirm
if [[ ! $confirm =~ ^[Yy]$ ]]; then
    echo "取消匯入"
    exit 0
fi

echo "開始匯入..."

# 匯入資料
if command -v mariadb >/dev/null 2>&1; then
    # 使用 MariaDB 客戶端
    mariadb -u "$DB_USER" -p -h "$DB_HOST" -P "$DB_PORT" "$DB_NAME" < "$SQL_FILE"
elif command -v mysql >/dev/null 2>&1; then
    # 使用 MySQL 客戶端
    mysql -u "$DB_USER" -p -h "$DB_HOST" -P "$DB_PORT" "$DB_NAME" < "$SQL_FILE"
else
    echo "錯誤: 找不到 MariaDB 或 MySQL 客戶端"
    echo "請安裝 MariaDB 或 MySQL 客戶端"
    exit 1
fi

if [ $? -eq 0 ]; then
    echo "✅ 題目資料匯入成功！"
else
    echo "❌ 題目資料匯入失敗"
    exit 1
fi