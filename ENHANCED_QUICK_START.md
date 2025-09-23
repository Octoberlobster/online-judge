# DMOJ 增強版 CSV 題目匯入 - 快速開始

## 檔案說明

本次更新包含以下檔案：

### 1. 主要腳本
- **`enhanced_bulk_import_problems.py`** - 增強版題目批量匯入腳本
- **`test_enhanced_import.py`** - 測試腳本

### 2. 範例和文檔
- **`enhanced_sample_data.csv`** - 範例 CSV 資料
- **`ENHANCED_BULK_IMPORT_GUIDE.md`** - 詳細使用指南
- **`ENHANCED_QUICK_START.md`** - 此快速開始指南

### 3. CSV 格式檔案
- **`enhanced_sample_problems (1).csv`** - 空白 CSV 模板

## 快速測試

### 1. 執行測試腳本
```bash
cd /home/xc/dmoj-site
python test_enhanced_import.py
```

### 2. 使用範例資料測試
```bash
# 試運行（不實際修改資料庫）
python enhanced_bulk_import_problems.py --csv enhanced_sample_data.csv --dry-run

# 實際匯入
python enhanced_bulk_import_problems.py --csv enhanced_sample_data.csv
```

## CSV 格式重點

### 基本欄位（必填）
```csv
code,name,group
sample001,測試題目,basic
```

### 完整欄位（42個欄位）
參考 `enhanced_sample_data.csv` 或 `enhanced_sample_problems (1).csv`

### 重要欄位說明

#### Verilog 特色功能
```csv
enable_waveform,enable_ppa,ppa_maximum_fmax,f4pga_board,openlane_pdk
true,true,350.0,basys3,sky130A
```

#### 多語言翻譯
```csv
translation_en_name,translation_zh_hant_name
"Simple Adder","簡單加法器"
```

#### 解答內容
```csv
solution_content,solution_is_public
"module solution(); endmodule",true
```

#### 澄清和語言限制
```csv
clarifications,language_limits
"請注意時序;確保穩定","Verilog:3.0:524288"
```

## 新功能特色

### 1. 完整的資料庫欄位支援
- ✅ 所有 42 個 CSV 欄位對應到資料庫表
- ✅ Verilog/FPGA 特色功能完全支援
- ✅ 多對多關係自動處理

### 2. 增強的資料處理
- ✅ 智能型別轉換（布林、數值、列表）
- ✅ 容錯處理（找不到使用者/語言時警告）
- ✅ 多分隔符支援（逗號、分號）

### 3. 多語言翻譯支援
- ✅ 英文翻譯 (`translation_en_*`)
- ✅ 繁體中文翻譯 (`translation_zh_hant_*`)
- ✅ 自動創建/更新翻譯記錄

### 4. 解答系統整合
- ✅ 解答內容匯入
- ✅ 解答可見性設定
- ✅ 解答作者關聯

### 5. 進階功能
- ✅ 題目澄清批量匯入
- ✅ 語言特定限制設定
- ✅ 完整的日誌記錄

## 與舊版本的差異

| 功能 | 舊版本 | 新版本 |
|------|--------|--------|
| CSV 欄位數量 | ~15 個 | 42 個 |
| Verilog 支援 | 基本 | 完整 |
| 翻譯支援 | 無 | 多語言 |
| 解答匯入 | 無 | 完整 |
| 錯誤處理 | 基本 | 增強 |
| 測試支援 | 無 | 完整 |

## 資料庫結構對應

腳本根據以下資料庫表結構設計：

### 主表
- `judge_problem` - 主要題目資訊
- `judge_problemtranslation` - 翻譯
- `judge_solution` - 解答
- `judge_problemclarification` - 澄清
- `judge_languagelimit` - 語言限制

### 關聯表
- `judge_problem_authors` - 作者關聯
- `judge_problem_types` - 類型關聯
- `judge_problem_allowed_languages` - 語言關聯
- 其他多對多關聯表

## 故障排除

### 常見問題

1. **Django 匯入錯誤**
   ```bash
   cd /home/xc/dmoj-site
   export DJANGO_SETTINGS_MODULE=dmoj.settings
   ```

2. **找不到使用者**
   - 確保使用者存在於系統中
   - 檢查使用者名稱拼寫

3. **找不到語言**
   - 確保語言已在 DMOJ 中定義
   - 使用正確的語言 key

4. **權限問題**
   ```bash
   chmod +x enhanced_bulk_import_problems.py
   ```

### 日誌檢查
```bash
tail -f enhanced_bulk_import.log
```

## 下一步

1. 閱讀完整指南：`ENHANCED_BULK_IMPORT_GUIDE.md`
2. 準備你的 CSV 資料
3. 使用 `--dry-run` 進行測試
4. 備份資料庫後執行實際匯入

## 支援

- 檢查日誌檔案：`enhanced_bulk_import.log`
- 使用測試腳本驗證功能
- 參考範例 CSV 檔案格式