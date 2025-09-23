# DMOJ 增強版題目批量匯入指南

## 概述

`enhanced_bulk_import_problems.py` 是一個功能完整的 DMOJ 題目批量匯入工具，專門針對 `enhanced_sample_problems.csv` 格式設計，支援所有題目相關功能。

## 功能特色

- ✅ 完整的題目資訊匯入（42個欄位）
- ✅ Verilog/FPGA 特色功能支援
- ✅ 多語言翻譯（英文、繁體中文）
- ✅ 解答內容匯入
- ✅ 題目澄清匯入
- ✅ 語言特定限制設定
- ✅ 多對多關係處理
- ✅ 完整的錯誤處理和日誌記錄
- ✅ 試運行模式

## 安裝要求

```bash
# 確保在 DMOJ 環境中運行
cd /path/to/dmoj-site
source venv/bin/activate  # 如果使用虛擬環境
```

## 使用方法

### 基本用法

```bash
# 匯入題目
python enhanced_bulk_import_problems.py --csv enhanced_sample_data.csv

# 試運行（不實際修改資料庫）
python enhanced_bulk_import_problems.py --csv data.csv --dry-run

# 跳過錯誤繼續處理
python enhanced_bulk_import_problems.py --csv data.csv --skip-errors

# 設定日誌等級
python enhanced_bulk_import_problems.py --csv data.csv --log-level DEBUG
```

### 參數說明

| 參數 | 必填 | 說明 |
|------|------|------|
| `--csv` | ✅ | CSV 檔案路徑 |
| `--dry-run` | ❌ | 試運行模式，不實際修改資料庫 |
| `--skip-errors` | ❌ | 遇到錯誤時跳過繼續處理 |
| `--log-level` | ❌ | 日誌等級 (DEBUG/INFO/WARNING/ERROR) |

## CSV 格式說明

### 必填欄位

| 欄位 | 說明 | 範例 |
|------|------|------|
| `code` | 題目代碼（唯一） | `sample001` |
| `name` | 題目名稱 | `簡單加法器` |
| `group` | 題目群組 | `basic` |

### 基本設定欄位

| 欄位 | 類型 | 說明 | 預設值 |
|------|------|------|--------|
| `description` | 文字 | 題目描述 | 空字串 |
| `time_limit` | 浮點數 | 時間限制（秒） | 1.0 |
| `memory_limit` | 整數 | 記憶體限制（KB） | 262144 |
| `points` | 浮點數 | 題目分數 | 1.0 |
| `is_public` | 布林 | 是否公開 | false |
| `partial` | 布林 | 允許部分分數 | false |
| `short_circuit` | 布林 | 短路評判 | false |
| `is_manually_managed` | 布林 | 手動管理 | false |
| `is_full_markup` | 布林 | 完整標記語言 | false |

### 關聯欄位（多個值用逗號分隔）

| 欄位 | 說明 | 範例 |
|------|------|------|
| `types` | 題目類型 | `Combinational Logic,Basic` |
| `authors` | 作者使用者名稱 | `admin,user1` |
| `curators` | 策展人使用者名稱 | `curator1,curator2` |
| `testers` | 測試者使用者名稱 | `tester1` |
| `allowed_languages` | 允許語言 | `Verilog,SystemVerilog` |
| `banned_users` | 禁用使用者 | `banned_user1` |
| `organizations` | 組織 | `org1,org2` |

### Verilog/FPGA 特色欄位

| 欄位 | 類型 | 說明 |
|------|------|------|
| `enable_waveform` | 布林 | 啟用波形圖 |
| `enable_ppa` | 布林 | 啟用 PPA 分析 |
| `ppa_maximum_fmax` | 浮點數 | 最大 Fmax（MHz） |
| `f4pga_board` | 字串 | F4PGA 開發板 |
| `f4pga_target_fmax` | 浮點數 | F4PGA 目標頻率 |
| `openlane_pdk` | 字串 | OpenLane PDK |
| `openlane_ppa_score` | 浮點數 | PPA 分數 |
| `openlane_critical_path_ns` | 浮點數 | 關鍵路徑延遲 |
| `openlane_core_area_um2` | 浮點數 | 核心面積 |
| `openlane_power_total` | 浮點數 | 總功耗 |

#### F4PGA 開發板選項
- `basys3` - Basys3
- `arty_a7_35t` - Arty A7-35T
- `arty_a7_100t` - Arty A7-100T
- `nexys4_ddr` - Nexys 4 DDR
- `nexys_video` - Nexys Video
- `zybo_z7` - Zybo Z7

#### OpenLane PDK 選項
- `sky130A` - sky130A
- `sky130B` - sky130B
- `gf180mcuC` - gf180mcuC

### 解答相關欄位

| 欄位 | 類型 | 說明 |
|------|------|------|
| `solution_content` | 文字 | 解答內容 |
| `solution_is_public` | 布林 | 解答是否公開 |
| `solution_authors` | 字串 | 解答作者（逗號分隔） |

### 多語言翻譯欄位

| 欄位 | 說明 |
|------|------|
| `translation_en_name` | 英文題目名稱 |
| `translation_en_description` | 英文題目描述 |
| `translation_zh_hant_name` | 繁體中文題目名稱 |
| `translation_zh_hant_description` | 繁體中文題目描述 |

### 特殊欄位

| 欄位 | 格式 | 說明 |
|------|------|------|
| `clarifications` | 文字（分號分隔） | 題目澄清 |
| `language_limits` | `語言:時間:記憶體;語言:時間:記憶體` | 語言特定限制 |

### 布林值格式

以下值會被解析為 `true`：
- `true`, `1`, `yes`, `on`, `enabled`, `是`, `啟用`

其他值或空值都會被解析為 `false`。

## 範例 CSV 行

```csv
code,name,description,group,time_limit,memory_limit,points,types,authors,curators,testers,allowed_languages,is_public,partial,short_circuit,is_manually_managed,license,og_image,summary,banned_users,organizations,is_organization_private,enable_waveform,enable_ppa,ppa_maximum_fmax,f4pga_board,f4pga_target_fmax,openlane_pdk,openlane_ppa_score,openlane_critical_path_ns,openlane_core_area_um2,openlane_power_total,solution_content,solution_is_public,solution_authors,translation_en_name,translation_en_description,translation_zh_hant_name,translation_zh_hant_description,clarifications,language_limits,is_full_markup
sample001,簡單加法器,設計一個簡單的加法器電路,basic,2.0,262144,5.0,Combinational Logic,admin,,,"Verilog,SystemVerilog",true,false,false,false,,,這是一個基本的加法器題目,,default,false,true,true,350.0,basys3,300.0,sky130A,4.5,2.5,50000.0,0.000001,"module solution(); endmodule",true,admin,"Simple Adder","Design a simple adder circuit",簡單加法器,設計一個簡單的加法器電路,請注意輸入信號的時序;確保輸出信號穩定,Verilog:3.0:524288,false
```

## 錯誤處理

### 常見錯誤

1. **找不到使用者**: 確保 `authors`, `curators`, `testers` 中的使用者名稱存在
2. **找不到語言**: 確保 `allowed_languages` 中的語言在系統中已定義
3. **找不到組織**: 確保 `organizations` 中的組織 slug 正確
4. **數值格式錯誤**: 確保數值欄位格式正確

### 日誌檔案

執行時會生成 `enhanced_bulk_import.log` 檔案，包含詳細的執行記錄。

## 安全注意事項

1. **備份資料庫**: 在執行批量匯入前請備份資料庫
2. **使用試運行**: 先使用 `--dry-run` 參數驗證
3. **權限檢查**: 確保執行用戶有足夠的資料庫權限
4. **檔案編碼**: CSV 檔案應使用 UTF-8 編碼

## 效能優化

- 大量匯入時建議使用 `--skip-errors` 參數
- 可以分批次匯入大型 CSV 檔案
- 匯入期間避免其他大量資料庫操作

## 故障排除

### 1. Django 匯入錯誤
```bash
# 確保在正確的目錄中運行
cd /path/to/dmoj-site
python enhanced_bulk_import_problems.py --csv data.csv
```

### 2. 權限錯誤
```bash
# 確保有執行權限
chmod +x enhanced_bulk_import_problems.py
```

### 3. 編碼問題
確保 CSV 檔案使用 UTF-8 編碼，Excel 儲存時選擇 "UTF-8 CSV"。

### 4. 記憶體不足
大型檔案可以分割後分批匯入：
```bash
# 分割 CSV 檔案
split -l 1000 large_file.csv part_
```

## 支援

如有問題請查看：
1. 執行日誌：`enhanced_bulk_import.log`
2. Django 日誌
3. 資料庫日誌

---

**注意**: 此工具會直接修改 DMOJ 資料庫，請在使用前務必備份資料並在測試環境中驗證。