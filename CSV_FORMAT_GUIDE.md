# CSV 格式說明範例

## 📋 完整欄位列表

### 基本欄位 (必填)
```
code                - 題目代碼 (小寫字母、數字、下劃線)
name                - 題目名稱
description         - 題目描述
group               - 題目組別 (Demo, NVIDIA, Uncategorized)
time_limit          - 時間限制 (秒，如 1.0, 2.5)
memory_limit        - 記憶體限制 (KB，如 262144)
points              - 分數 (如 100, 150)
```

### 可選欄位
```
types               - 題目類型 (Traditional, Math, Implementation, Dynamic Programming, verilog)
authors             - 作者 (用戶名，多個用逗號分隔)
allowed_languages   - 允許語言 (Verilog, C, C++, Python 等，逗號分隔)
is_public           - 是否公開 (true/false)
partial             - 部分分數 (true/false)
short_circuit       - 短路評測 (true/false)
```

### 題解欄位 (新增功能)
```
solution_content    - 題解內容 (支援 Markdown 格式)
solution_is_public  - 題解是否公開 (true/false)
solution_publish_on - 題解發布日期 (YYYY-MM-DD HH:MM:SS)
solution_authors    - 題解作者 (用戶名，多個用逗號分隔)
```

### 翻譯欄位 (新增功能)
```
translations        - 多語言翻譯 (格式: 語言代碼:標題:描述,語言代碼:標題:描述)
                     支援語言: en (英文), zh-hant (繁體中文)
```

## 📝 範例說明

### 基本題目 (無題解無翻譯)
```csv
code,name,description,group,time_limit,memory_limit,points,types,authors,allowed_languages,is_public,partial,short_circuit,solution_content,solution_is_public,solution_publish_on,solution_authors,translations
hello,Hello World,輸出 Hello World,Demo,1.0,262144,100,Traditional,,Verilog,true,false,false,,,,
```

### 包含題解的題目
```csv
code,name,description,group,time_limit,memory_limit,points,types,authors,allowed_languages,is_public,partial,short_circuit,solution_content,solution_is_public,solution_publish_on,solution_authors,translations
hello,Hello World,輸出 Hello World,Demo,1.0,262144,100,Traditional,,Verilog,true,false,false,"這是解題說明...",true,2025-09-01 12:00:00,,
```

### 包含翻譯的題目
```csv
code,name,description,group,time_limit,memory_limit,points,types,authors,allowed_languages,is_public,partial,short_circuit,solution_content,solution_is_public,solution_publish_on,solution_authors,translations
hello,Hello World,輸出 Hello World,Demo,1.0,262144,100,Traditional,,Verilog,true,false,false,,,,,"en:Hello World:Output Hello World,zh-hant:哈囉世界:輸出哈囉世界"
```

### 完整功能題目
```csv
code,name,description,group,time_limit,memory_limit,points,types,authors,allowed_languages,is_public,partial,short_circuit,solution_content,solution_is_public,solution_publish_on,solution_authors,translations
hello,Hello World,輸出 Hello World,Demo,1.0,262144,100,Traditional,,Verilog,true,false,false,"完整的解題說明...",true,2025-09-01 12:00:00,,"en:Hello World:Output Hello World,zh-hant:哈囉世界:輸出哈囉世界"
```

## ⚠️ 重要注意事項

1. **CSV 編碼**：請使用 UTF-8 編碼保存
2. **引號處理**：如果內容包含逗號或換行，請用雙引號包圍
3. **換行符號**：題解內容中的換行請使用實際換行，不要用 \n
4. **空欄位**：可選欄位可以留空，但不能省略欄位
5. **日期格式**：支援 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS

## 🔍 驗證檢查

匯入前系統會檢查：
- 題目代碼唯一性
- 組別和類型是否存在
- 時間和記憶體限制合理性
- 語言代碼有效性
- 日期格式正確性
