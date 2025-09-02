# 郵件域名註冊限制管理功能

## 功能簡介

此功能允許管理員通過Django管理界面管理允許註冊的郵件域名，取代了原先硬編碼的`.edu.tw`限制。

## 主要特性

### 1. 管理員界面管理
- 在Django管理後台中新增、編輯、刪除允許的郵件域名
- 可以啟用/停用特定域名
- 支援搜尋和過濾功能
- 顯示創建和更新時間

### 2. 靈活的域名匹配
- 支援完整域名匹配（如：`gmail.com`）
- 支援子域名匹配（如：`ntu.edu.tw` 可以匹配 `edu.tw` 設定）
- 不區分大小寫

### 3. 向後兼容
- 如果沒有設定任何允許域名，系統會自動使用原來的`.edu.tw`限制
- 保留原有的郵件黑名單檢查功能

## 使用方法

### 管理員界面操作

1. **登入管理後台**
   - 訪問 `/admin/` 
   - 使用管理員帳號登入

2. **管理允許的郵件域名**
   - 在管理界面中找到 "Allowed email domains" 選項
   - 點擊進入域名管理頁面

3. **新增域名**
   - 點擊 "Add allowed email domain"
   - 輸入域名（如：`edu.tw`, `gmail.com`）
   - 添加描述（可選）
   - 確保 "Is active" 為勾選狀態
   - 點擊保存

4. **編輯或刪除域名**
   - 在列表中點擊要編輯的域名
   - 修改資訊或點擊刪除按鈕

### 命令行操作

1. **設置默認域名**
   ```bash
   python manage.py setup_email_domains --default
   ```

2. **添加自定義域名**
   ```bash
   python manage.py setup_email_domains --domain example.com --domain university.edu
   ```

3. **清除所有域名並重新設置**
   ```bash
   python manage.py setup_email_domains --clear --default
   ```

## 測試驗證

執行測試腳本驗證功能：
```bash
python test_email_domains.py
```

## 設定檔案說明

### 新增的檔案

1. **`judge/models/registration.py`** - 郵件域名模型定義
2. **`judge/admin/registration.py`** - 管理員界面配置
3. **`judge/management/commands/setup_email_domains.py`** - 設置命令
4. **`test_email_domains.py`** - 測試腳本

### 修改的檔案

1. **`judge/models/__init__.py`** - 添加新模型的導入
2. **`judge/admin/__init__.py`** - 註冊管理員界面
3. **`judge/views/register.py`** - 更新註冊驗證邏輯

## 資料庫結構

### AllowedEmailDomain 模型欄位

- `domain` (CharField) - 郵件域名（如：edu.tw）
- `description` (CharField) - 域名描述（可選）
- `is_active` (BooleanField) - 是否啟用
- `created_at` (DateTimeField) - 創建時間
- `updated_at` (DateTimeField) - 更新時間

## 示例用法

### 允許多個教育機構域名
```python
# 透過管理界面或命令添加：
# edu.tw - 台灣教育機構
# edu.cn - 中國教育機構  
# ac.uk - 英國教育機構
```

### 允許特定企業郵件
```python
# 透過管理界面添加：
# company.com - 公司內部郵件
# partner.org - 合作夥伴組織
```

## 注意事項

1. 域名匹配不區分大小寫
2. 支援子域名匹配（如：`mail.edu.tw` 會匹配 `edu.tw` 設定）
3. 如果沒有任何啟用的域名，系統會回退到原來的 `.edu.tw` 限制
4. 建議在生產環境中先測試新的域名設定
5. 可以隨時通過管理界面停用特定域名而不需要刪除

## 故障排除

1. **檢查域名設定**
   ```bash
   python manage.py shell
   >>> from judge.models import AllowedEmailDomain
   >>> AllowedEmailDomain.objects.filter(is_active=True)
   ```

2. **測試特定郵件**
   ```bash
   python manage.py shell
   >>> from judge.models import AllowedEmailDomain
   >>> AllowedEmailDomain.is_domain_allowed('test@example.com')
   ```

3. **查看錯誤日誌**
   - 檢查Django日誌中的註冊錯誤訊息
   - 確認資料庫遷移已正確執行
