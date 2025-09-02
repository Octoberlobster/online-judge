# CSV 題目匯入功能 - 支援題解和翻譯

## 🎉 新增功能

現在 CSV 匯入功能已完全支援：
- ✅ 基本題目資訊匯入
- ✅ **題解內容匯入** (新增)
- ✅ **多語言翻譯匯入** (新增)
- ✅ Verilog 語言支援
- ✅ 完整的管理員介面整合

## 📋 CSV 格式規範

### 基本欄位 (必填)
- `code`: 題目代碼 (小寫字母、數字、下劃線)
- `name`: 題目名稱
- `description`: 題目描述
- `group`: 題目組別 (必須已存在)
- `time_limit`: 時間限制 (秒)
- `memory_limit`: 記憶體限制 (KB)
- `points`: 分數

### 可選欄位
- `types`: 題目類型 (逗號分隔)
- `authors`: 作者 (逗號分隔的用戶名)
- `allowed_languages`: 允許的程式語言 (逗號分隔)
- `is_public`: 是否公開 (true/false)
- `partial`: 支援部分分數 (true/false)
- `short_circuit`: 短路評測 (true/false)

### 題解欄位 (新增)
- `solution_content`: 題解內容 (支援 Markdown)
- `solution_is_public`: 題解是否公開 (true/false)
- `solution_publish_on`: 題解發布日期 (YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS)
- `solution_authors`: 題解作者 (逗號分隔的用戶名)

### 翻譯欄位 (新增)
- `translations`: 翻譯內容，格式：`語言代碼:翻譯名稱:翻譯描述,語言代碼:翻譯名稱:翻譯描述`

## 📝 CSV 範例

```csv
code,name,description,group,time_limit,memory_limit,points,types,authors,allowed_languages,is_public,partial,short_circuit,solution_content,solution_is_public,solution_publish_on,solution_authors,translations
hello_advanced,Hello World 進階版,要求輸出 Hello World 並包含換行,Demo,1.0,262144,100,Traditional,,Verilog,true,false,false,"這個問題很簡單，只需要使用基本的輸出功能即可解決。

**解題思路：**
1. 使用基本的輸出語法
2. 確保包含正確的換行字符

**Verilog 範例代碼：**
```verilog
module hello_world;
    initial begin
        $display(""Hello World"");
        $finish;
    end
endmodule
```",true,2025-09-01 12:00:00,,"en:Hello World Advanced:Output Hello World with newline,zh-hant:Hello World 進階版:要求輸出 Hello World 並包含換行"
```

## 🌍 支援的語言代碼

- `en`: English (英文)
- `zh-hant`: Traditional Chinese (繁體中文)

## 🚀 使用方式

1. **登入管理員介面**：訪問 `/admin/`
2. **找到 CSV 匯入**：
   - 點擊左側選單的 **"題目"** 區塊
   - 選擇 **"CSV 匯入助手"**
3. **上傳並預覽**：
   - 上傳 CSV 檔案
   - 點擊 "上傳並預覽" 查看將匯入的內容
4. **確認匯入**：
   - 檢查預覽資料無誤後
   - 點擊 "確認匯入" 完成批量匯入

## 🔍 驗證規則

### 題目代碼
- 必須是小寫字母、數字、下劃線組成
- 不能與現有題目重複

### 題解
- 支援 Markdown 格式
- 可設定公開狀態和發布日期
- 可指定多個作者

### 翻譯
- 必須使用系統支援的語言代碼
- 名稱和描述都不能為空
- 支援多語言同時匯入

## ⚠️ 注意事項

1. **檔案大小限制**：最大 5MB
2. **編碼格式**：使用 UTF-8 編碼
3. **資料驗證**：匯入前會驗證所有資料
4. **事務處理**：使用資料庫事務，確保資料一致性
5. **預覽功能**：建議先預覽再正式匯入

## 🎯 進階功能

- **批量題解**：一次匯入多個題目的完整題解
- **多語言支援**：自動創建題目的多語言版本
- **作者管理**：支援多作者協作
- **發布控制**：可設定題解的發布時間
