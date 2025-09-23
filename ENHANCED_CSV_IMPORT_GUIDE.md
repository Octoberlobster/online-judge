# DMOJ 增強版 CSV 匯入功能說明

## 📊 概述

本增強版 CSV 匯入功能支援匯入完整的題目資料，包括基本資訊、翻譯、澄清說明、語言限制、解答等所有相關資料表。

## 🎯 支援的欄位

### 基本資訊欄位
| 欄位名稱 | 類型 | 必填 | 說明 |
|---------|------|------|------|
| `code` | 字串 | ✅ | 題目代碼，唯一識別碼 |
| `name` | 字串 | ✅ | 題目名稱 |
| `description` | 文字 | ✅ | 題目描述內容 |
| `group` | 字串 | ✅ | 題目群組名稱 |
| `time_limit` | 浮點數 | ✅ | 時間限制（秒） |
| `memory_limit` | 整數 | ✅ | 記憶體限制（KB） |
| `points` | 浮點數 | ✅ | 題目分數 |
| `is_public` | 布林值 | ❌ | 是否公開 |
| `partial` | 布林值 | ❌ | 是否允許部分分數 |
| `short_circuit` | 布林值 | ❌ | 短路模式 |
| `is_manually_managed` | 布林值 | ❌ | 是否手動管理 |
| `summary` | 字串 | ❌ | 題目摘要 |
| `og_image` | 字串 | ❌ | OpenGraph 圖片 URL |

### 分類與權限欄位
| 欄位名稱 | 類型 | 必填 | 說明 |
|---------|------|------|------|
| `types` | 字串 | ❌ | 題目類型，用逗號分隔 |
| `license` | 字串 | ❌ | 許可證代碼 |
| `allowed_languages` | 字串 | ❌ | 允許的程式語言，用逗號分隔 |
| `authors` | 字串 | ❌ | 作者用戶名，用逗號分隔 |
| `curators` | 字串 | ❌ | 策劃者用戶名，用逗號分隔 |
| `testers` | 字串 | ❌ | 測試者用戶名，用逗號分隔 |
| `banned_users` | 字串 | ❌ | 禁用用戶名，用逗號分隔 |
| `organizations` | 字串 | ❌ | 組織名稱，用逗號分隔 |
| `is_organization_private` | 布林值 | ❌ | 是否為組織私有 |

### Verilog 專用欄位
| 欄位名稱 | 類型 | 必填 | 說明 |
|---------|------|------|------|
| `enable_waveform` | 布林值 | ❌ | 是否啟用波形處理 |
| `enable_ppa` | 布林值 | ❌ | 是否啟用 PPA 計算 |
| `ppa_maximum_fmax` | 浮點數 | ❌ | 最大 PPA 頻率 (MHz) |
| `f4pga_board` | 字串 | ❌ | F4PGA 開發板 |
| `f4pga_target_fmax` | 浮點數 | ❌ | F4PGA 目標頻率 (MHz) |
| `openlane_pdk` | 字串 | ❌ | OpenLane PDK |
| `openlane_ppa_score` | 浮點數 | ❌ | OpenLane PPA 分數 |
| `openlane_critical_path_ns` | 浮點數 | ❌ | OpenLane 關鍵路徑 (ns) |
| `openlane_core_area_um2` | 浮點數 | ❌ | OpenLane 核心面積 (um²) |
| `openlane_power_total` | 浮點數 | ❌ | OpenLane 總功耗 |

### 內容欄位
| 欄位名稱 | 類型 | 必填 | 說明 |
|---------|------|------|------|
| `translations` | 字串 | ❌ | 翻譯資料 |
| `clarifications` | 字串 | ❌ | 澄清說明 |
| `language_limits` | 字串 | ❌ | 語言限制 |
| `solution_content` | 文字 | ❌ | 解答內容 |
| `solution_is_public` | 布林值 | ❌ | 解答是否公開 |
| `solution_authors` | 字串 | ❌ | 解答作者用戶名，用逗號分隔 |

## 📝 特殊格式說明

### 翻譯格式 (translations)
```
語言代碼:翻譯標題:翻譯描述|語言代碼:翻譯標題:翻譯描述
```
**範例:**
```
en:Hello World:Output the string Hello World|zh-hant:哈囉世界:輸出字串 Hello World
```

### 澄清說明格式 (clarifications)
```
澄清說明1|澄清說明2|澄清說明3
```
**範例:**
```
請注意輸出格式要完全正確|記得加上換行符號
```

### 語言限制格式 (language_limits)
```
語言代碼:時間限制:記憶體限制|語言代碼:時間限制:記憶體限制
```
**範例:**
```
V:3.0:524288|SV:1.5:262144
```

### 布林值格式
支援以下值：
- **True**: `true`, `1`, `yes`, `on`
- **False**: `false`, `0`, `no`, `off`

## 🚀 使用方法

### 1. 準備 CSV 檔案
創建一個 UTF-8 編碼的 CSV 檔案，包含必要的欄位。

### 2. 通過 Admin 介面匯入
1. 登入 Django Admin
2. 進入 Problems 頁面
3. 點擊 "匯入 CSV 文件"
4. 上傳 CSV 檔案
5. 點擊 "Preview" 預覽結果
6. 確認無誤後點擊 "Import" 正式匯入

### 3. 下載範例檔案
在 Admin 的匯入頁面可以下載包含所有欄位的範例 CSV 檔案。

## 📋 完整範例

```csv
code,name,description,group,time_limit,memory_limit,points,types,allowed_languages,is_public,partial,enable_waveform,enable_ppa,license,summary,translations,clarifications
hello_world,Hello World,輸出 Hello World 字串,Demo,1.0,262144,100,Traditional,V,true,false,true,false,CC0-1.0,簡單的測試題目,"en:Hello World:Output the string Hello World|zh-hant:哈囉世界:輸出字串 Hello World","請注意輸出格式|記得加上換行符號"
fpga_counter,FPGA計數器,設計一個8位元計數器,Demo,3.0,524288,200,Implementation,V,true,true,true,true,,FPGA設計挑戰,"en:FPGA Counter:Design an 8-bit counter|zh-hant:FPGA計數器:設計一個8位元計數器","需要支援重置功能|頻率要達到100MHz"
```

## ⚠️ 注意事項

1. **編碼**: CSV 檔案必須使用 UTF-8 編碼
2. **唯一性**: 題目代碼 (code) 必須唯一
3. **依賴關係**: 引用的群組、類型、語言、用戶等必須已存在
4. **檔案大小**: 單個 CSV 檔案限制 10MB
5. **欄位順序**: 欄位順序不重要，但標題行必須正確

## 🔧 錯誤處理

匯入過程中如果遇到錯誤，系統會：
1. 停止處理並回滾所有變更
2. 顯示具體的錯誤訊息和行號
3. 不會部分匯入，確保資料一致性

## 📊 支援的資料表

此功能可以一次性創建以下所有相關資料：
- ✅ Problem (題目主表)
- ✅ ProblemTranslation (翻譯)
- ✅ ProblemClarification (澄清說明)
- ✅ LanguageLimit (語言限制)
- ✅ Solution (解答)
- ✅ 多對多關係 (類型、作者、語言等)

這個增強版功能大大簡化了題目的批量匯入工作，特別適合需要大量創建題目的場景。