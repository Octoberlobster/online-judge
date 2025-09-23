# DMOJ 題目資料匯出/匯入指南

## 📦 匯出題目資料

### 已完成的匯出
✅ 題目資料已成功匯出到 `dmoj_problems_export.sql`

- **檔案大小**: 900K
- **檔案行數**: 1,524 行
- **匯出日期**: 2025-09-17 23:37:33
- **包含表格**: 15 個題目相關資料表

### 匯出的資料表
1. **主要資料表**:
   - `judge_problem` - 題目主表
   - `judge_problemtranslation` - 題目翻譯
   - `judge_problemclarification` - 題目澄清
   - `judge_problemtype` - 題目類型
   - `judge_problemgroup` - 題目群組
   - `judge_languagelimit` - 語言限制
   - `judge_solution` - 官方解答
   - `judge_license` - 授權許可

2. **多對多關係表**:
   - `judge_problem_authors` - 題目作者
   - `judge_problem_curators` - 題目策展人
   - `judge_problem_testers` - 題目測試者
   - `judge_problem_types` - 題目類型關係
   - `judge_problem_allowed_languages` - 允許語言
   - `judge_problem_banned_users` - 禁用使用者
   - `judge_problem_organizations` - 組織關係

## 📥 匯入題目資料到另一台機器

### 方法一：使用自動化腳本（推薦）

1. **複製檔案到目標機器**:
   ```bash
   # 將以下檔案複製到目標機器
   scp dmoj_problems_export.sql user@target-server:/path/to/dmoj-site/
   scp import_problems.sh user@target-server:/path/to/dmoj-site/
   ```

2. **執行匯入腳本**:
   ```bash
   cd /path/to/dmoj-site/
   chmod +x import_problems.sh
   ./import_problems.sh [資料庫名稱] [使用者名稱] [主機] [埠號]
   ```

   **範例**:
   ```bash
   # 使用預設設定 (localhost:3306, dmoj 資料庫, dmoj 使用者)
   ./import_problems.sh
   
   # 自訂設定
   ./import_problems.sh dmoj xc 127.0.0.1 3306
   ```

### 方法二：手動匯入

1. **使用 MariaDB 客戶端**:
   ```bash
   mariadb -u 使用者名稱 -p -h 主機地址 -P 埠號 資料庫名稱 < dmoj_problems_export.sql
   ```

2. **使用 MySQL 客戶端**:
   ```bash
   mysql -u 使用者名稱 -p -h 主機地址 -P 埠號 資料庫名稱 < dmoj_problems_export.sql
   ```

## ⚠️ 重要注意事項

### 匯入前準備
1. **備份目標資料庫**:
   ```bash
   mariadb-dump -u 使用者 -p 資料庫名稱 > backup_before_import.sql
   ```

2. **確認目標 DMOJ 版本相容性**:
   - 確保目標機器的 DMOJ 版本與來源機器相同或相容
   - 檢查資料庫 schema 是否一致

3. **檢查權限**:
   - 確保匯入使用者有 INSERT, UPDATE, DELETE 權限
   - 檢查外鍵約束設定

### 匯入後檢查
1. **驗證資料完整性**:
   ```sql
   -- 檢查題目數量
   SELECT COUNT(*) FROM judge_problem;
   
   -- 檢查翻譯數量
   SELECT COUNT(*) FROM judge_problemtranslation;
   
   -- 檢查關係表
   SELECT COUNT(*) FROM judge_problem_authors;
   ```

2. **重新整理快取**:
   ```bash
   # 在 DMOJ 網站目錄執行
   python manage.py collectstatic --noinput
   python manage.py migrate
   ```

3. **重啟服務**:
   ```bash
   sudo supervisorctl restart all
   # 或
   sudo systemctl restart nginx
   sudo systemctl restart uwsgi
   ```

## 🔧 故障排除

### 常見問題

1. **外鍵約束錯誤**:
   - 確保目標資料庫已有相關的使用者、語言、組織等基礎資料
   - 可能需要先匯入基礎資料表

2. **字元編碼問題**:
   ```bash
   # 匯入時指定編碼
   mariadb -u user -p --default-character-set=utf8mb4 database < dmoj_problems_export.sql
   ```

3. **權限不足**:
   ```sql
   -- 授予必要權限
   GRANT ALL PRIVILEGES ON dmoj.* TO 'user'@'%';
   FLUSH PRIVILEGES;
   ```

4. **資料表已存在**:
   - SQL 檔案包含 DROP TABLE 和 CREATE TABLE 語句
   - 會覆蓋現有的題目資料，請謹慎操作

## 📊 匯出指令記錄

```bash
# 原始匯出指令
mariadb-dump -u xc -p --host=127.0.0.1 --port=3306 --single-transaction --routines --triggers dmoj \
  judge_problem \
  judge_problemtranslation \
  judge_problemclarification \
  judge_problemtype \
  judge_problemgroup \
  judge_languagelimit \
  judge_solution \
  judge_license \
  judge_problem_authors \
  judge_problem_curators \
  judge_problem_testers \
  judge_problem_types \
  judge_problem_allowed_languages \
  judge_problem_banned_users \
  judge_problem_organizations > dmoj_problems_export.sql
```

## 📈 後續步驟

匯入完成後建議：
1. 測試題目顯示和功能
2. 檢查 Verilog 特色功能（波形圖、PPA 等）
3. 驗證使用者權限和存取控制
4. 確認測資檔案完整性（可能需要另外複製）