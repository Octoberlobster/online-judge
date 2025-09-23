# CSV 匯入格式說明

## 概述

這個文件說明 DMOJ 題目 CSV 匯入的格式和使用方法。

## 基本欄位

### 必填欄位
- `code`: 題目代碼（最長 100 字元）
- `name`: 題目名稱
- `description`: 題目描述
- `group`: 題目分組
- `time_limit`: 時間限制（秒）
- `memory_limit`: 記憶體限制（KB）
- `points`: 分數
- `types`: 題目類型（可選：Traditional, Implementation, Math, Simple Math, Dynamic Programming, verilog）
- `allowed_languages`: 允許的程式語言

### 可選欄位
- `authors`: 作者（以逗號分隔的使用者名稱）
- `curators`: 策展人
- `testers`: 測試人員
- `is_public`: 是否公開（true/false）
- `partial`: 是否允許部分分數（true/false）
- `short_circuit`: 是否短路評分（true/false）
- `is_manually_managed`: 是否手動管理（true/false）
- `summary`: 題目摘要

## Verilog 特有欄位

### 波形檢視
- `enable_waveform`: 啟用波形檢視（true/false）

### PPA 分析
- `enable_ppa`: 啟用 PPA 分析（true/false）
- `ppa_maximum_fmax`: 全域最大頻率限制（MHz）

### F4PGA 欄位
- `f4pga_board`: F4PGA 目標開發板（如：basys3, arty_a7_100t）
- `f4pga_target_fmax`: F4PGA 目標頻率（MHz）

### OpenLane 欄位
- `openlane_pdk`: OpenLane PDK（如：sky130A, sky130B）
- `openlane_ppa_score`: 最低 PPA 分數
- `openlane_critical_path_ns`: 最大關鍵路徑延遲（ns）
- `openlane_core_area_um2`: 最大核心面積（μm²）
- `openlane_power_total`: 最大總功耗（mW）

## 翻譯功能

### 翻譯格式
翻譯欄位 `translations` 使用以下格式：

```
語言代碼:標題:描述|語言代碼:標題:描述
```

### 支援的語言代碼
- `en`: 英文
- `zh-hant`: 繁體中文

### 範例
```
en:Hello World:Output the string Hello World|zh-hant:哈囉世界:輸出字串 Hello World
```

### 注意事項
- 使用 `|` 分隔不同語言的翻譯
- 使用 `:` 分隔語言代碼、標題和描述
- 確保描述中不包含 `|` 或 `:` 字元
- 空的翻譯欄位請留空，不要填入 `None`

## 智能功能啟用

系統會根據欄位內容自動啟用相關功能：

### 自動啟用 F4PGA
當以下條件滿足時自動啟用：
- `f4pga_board` 不為空
- `f4pga_target_fmax` 大於 0

### 自動啟用 OpenLane
當以下條件滿足時自動啟用：
- `openlane_pdk` 不為空
- 任何 OpenLane PPA 欄位有值

### 自動啟用 PPA 分析
當以下條件滿足時自動啟用：
- 啟用了 F4PGA 或 OpenLane
- 或手動設定 `enable_ppa` 為 true

## 範例檔案

查看 `enhanced_sample_problems.csv` 以獲得完整的範例。

## 常見問題

### 1. 翻譯沒有顯示
- 檢查翻譯格式是否正確
- 確保沒有填入字串 "None"
- 確認語言代碼是否正確（en, zh-hant）

### 2. PPA 功能沒有啟用
- 檢查相關欄位是否有正確的值
- F4PGA 需要 board 和 target_fmax
- OpenLane 需要 pdk 和至少一個 PPA 參數

### 3. 匯入失敗
- 檢查必填欄位是否都有值
- 確認題目類型是否存在
- 驗證使用者名稱和組織名稱是否正確

## 版本更新

- v1.0: 基本 CSV 匯入功能
- v1.1: 新增 Verilog PPA 功能支援
- v1.2: 修正翻譯解析問題，支援完整的多語言功能
