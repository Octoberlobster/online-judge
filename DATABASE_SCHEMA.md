# DMOJ 題目相關資料表結構文檔

## 概述

DMOJ 平台的題目系統包含以下主要資料表和多對多關係表。本文檔詳細列出各表的欄位結構，便於理解題目資料的組織方式。

## 主要資料表

### 1. JUDGE_PROBLEM（題目主表）

| 欄位名稱 | 資料型態 | 是否可空 | 說明 |
|---------|---------|---------|------|
| id | int(11) | NO | 主鍵，自動遞增 |
| code | varchar(100) | NO | 題目代碼，唯一 |
| name | varchar(100) | NO | 題目名稱 |
| description | longtext | NO | 題目描述內容 |
| time_limit | double | NO | 時間限制（秒） |
| memory_limit | int(10) unsigned | NO | 記憶體限制（KB） |
| short_circuit | tinyint(1) | NO | 短路評判 |
| points | double | NO | 題目分數 |
| partial | tinyint(1) | NO | 允許部分分數 |
| is_public | tinyint(1) | NO | 是否公開 |
| is_manually_managed | tinyint(1) | NO | 手動管理 |
| date | datetime(6) | YES | 發布日期 |
| og_image | varchar(150) | NO | OpenGraph 圖片 |
| summary | longtext | NO | 題目摘要 |
| user_count | int(11) | NO | 解題使用者數量 |
| ac_rate | double | NO | 通過率 |
| is_organization_private | tinyint(1) | NO | 組織私有 |
| group_id | int(11) | NO | 題目群組外鍵 |
| license_id | int(11) | YES | 授權許可外鍵 |
| is_full_markup | tinyint(1) | NO | 完整標記語言存取 |
| submission_source_visibility_mode | varchar(1) | NO | 提交原始碼可見性模式 |

#### Verilog 相關欄位
| 欄位名稱 | 資料型態 | 是否可空 | 說明 |
|---------|---------|---------|------|
| enable_waveform | tinyint(1) | NO | 啟用波形處理 |
| enable_ppa | tinyint(1) | NO | 啟用 PPA 計算 |
| ppa_maximum_fmax | double | YES | 最大 PPA Fmax（MHz） |
| f4pga_board | varchar(20) | NO | F4PGA 開發板 |
| f4pga_target_fmax | double | YES | F4PGA 目標頻率（MHz） |
| openlane_pdk | varchar(20) | NO | OpenLane PDK |
| openlane_ppa_score | double | YES | OpenLane PPA 分數 |
| openlane_critical_path_ns | double | YES | OpenLane 最大關鍵路徑延遲 |
| openlane_core_area_um2 | double | YES | OpenLane 最大核心面積 |
| openlane_power_total | double | YES | OpenLane 最大總功耗 |

### 2. JUDGE_PROBLEMTRANSLATION（題目翻譯表）

| 欄位名稱 | 資料型態 | 是否可空 | 說明 |
|---------|---------|---------|------|
| id | int(11) | NO | 主鍵，自動遞增 |
| language | varchar(7) | NO | 語言代碼 |
| name | varchar(100) | NO | 翻譯的題目名稱 |
| description | longtext | NO | 翻譯的題目描述 |
| problem_id | int(11) | NO | 題目外鍵 |

### 3. JUDGE_PROBLEMCLARIFICATION（題目澄清表）

| 欄位名稱 | 資料型態 | 是否可空 | 說明 |
|---------|---------|---------|------|
| id | int(11) | NO | 主鍵，自動遞增 |
| description | longtext | NO | 澄清內容 |
| date | datetime(6) | NO | 澄清日期 |
| problem_id | int(11) | NO | 題目外鍵 |

### 4. JUDGE_PROBLEMTYPE（題目類型表）

| 欄位名稱 | 資料型態 | 是否可空 | 說明 |
|---------|---------|---------|------|
| id | int(11) | NO | 主鍵，自動遞增 |
| name | varchar(20) | NO | 類型代碼，唯一 |
| full_name | varchar(100) | NO | 類型全名 |

### 5. JUDGE_PROBLEMGROUP（題目群組表）

| 欄位名稱 | 資料型態 | 是否可空 | 說明 |
|---------|---------|---------|------|
| id | int(11) | NO | 主鍵，自動遞增 |
| name | varchar(20) | NO | 群組代碼，唯一 |
| full_name | varchar(100) | NO | 群組全名 |

### 6. JUDGE_LANGUAGELIMIT（語言限制表）

| 欄位名稱 | 資料型態 | 是否可空 | 說明 |
|---------|---------|---------|------|
| id | int(11) | NO | 主鍵，自動遞增 |
| time_limit | double | NO | 特定語言時間限制 |
| memory_limit | int(11) | NO | 特定語言記憶體限制 |
| language_id | int(11) | NO | 語言外鍵 |
| problem_id | int(11) | NO | 題目外鍵 |

### 7. JUDGE_SOLUTION（解答表）

| 欄位名稱 | 資料型態 | 是否可空 | 說明 |
|---------|---------|---------|------|
| id | int(11) | NO | 主鍵，自動遞增 |
| is_public | tinyint(1) | NO | 是否公開 |
| publish_on | datetime(6) | NO | 發布時間 |
| content | longtext | NO | 解答內容 |
| problem_id | int(11) | NO | 題目外鍵（唯一） |

### 8. JUDGE_LICENSE（授權許可表）

| 欄位名稱 | 資料型態 | 是否可空 | 說明 |
|---------|---------|---------|------|
| id | int(11) | NO | 主鍵，自動遞增 |
| key | varchar(20) | NO | 授權代碼，唯一 |
| link | varchar(256) | NO | 授權連結 |
| name | varchar(256) | NO | 授權全名 |
| display | varchar(256) | NO | 顯示名稱 |
| icon | varchar(256) | NO | 圖示 URL |
| text | longtext | NO | 授權文字 |

## 多對多關係表

### 1. JUDGE_PROBLEM_AUTHORS（題目作者關係）

| 欄位名稱 | 資料型態 | 是否可空 | 說明 |
|---------|---------|---------|------|
| id | int(11) | NO | 主鍵，自動遞增 |
| problem_id | int(11) | NO | 題目外鍵 |
| profile_id | int(11) | NO | 使用者檔案外鍵 |

### 2. JUDGE_PROBLEM_CURATORS（題目策展人關係）

| 欄位名稱 | 資料型態 | 是否可空 | 說明 |
|---------|---------|---------|------|
| id | int(11) | NO | 主鍵，自動遞增 |
| problem_id | int(11) | NO | 題目外鍵 |
| profile_id | int(11) | NO | 使用者檔案外鍵 |

### 3. JUDGE_PROBLEM_TESTERS（題目測試者關係）

| 欄位名稱 | 資料型態 | 是否可空 | 說明 |
|---------|---------|---------|------|
| id | int(11) | NO | 主鍵，自動遞增 |
| problem_id | int(11) | NO | 題目外鍵 |
| profile_id | int(11) | NO | 使用者檔案外鍵 |

### 4. JUDGE_PROBLEM_TYPES（題目類型關係）

| 欄位名稱 | 資料型態 | 是否可空 | 說明 |
|---------|---------|---------|------|
| id | int(11) | NO | 主鍵，自動遞增 |
| problem_id | int(11) | NO | 題目外鍵 |
| problemtype_id | int(11) | NO | 題目類型外鍵 |

### 5. JUDGE_PROBLEM_ALLOWED_LANGUAGES（題目允許語言關係）

| 欄位名稱 | 資料型態 | 是否可空 | 說明 |
|---------|---------|---------|------|
| id | int(11) | NO | 主鍵，自動遞增 |
| problem_id | int(11) | NO | 題目外鍵 |
| language_id | int(11) | NO | 語言外鍵 |

### 6. JUDGE_PROBLEM_BANNED_USERS（題目禁用使用者關係）

| 欄位名稱 | 資料型態 | 是否可空 | 說明 |
|---------|---------|---------|------|
| id | int(11) | NO | 主鍵，自動遞增 |
| problem_id | int(11) | NO | 題目外鍵 |
| profile_id | int(11) | NO | 使用者檔案外鍵 |

### 7. JUDGE_PROBLEM_ORGANIZATIONS（題目組織關係）

| 欄位名稱 | 資料型態 | 是否可空 | 說明 |
|---------|---------|---------|------|
| id | int(11) | NO | 主鍵，自動遞增 |
| problem_id | int(11) | NO | 題目外鍵 |
| organization_id | int(11) | NO | 組織外鍵 |

## 資料表關係說明

1. **主表關係**：
   - `judge_problem` 是核心表，通過外鍵連接 `judge_problemgroup` 和 `judge_license`
   - `judge_problemtranslation` 提供多語言支援（一對多）
   - `judge_problemclarification` 儲存題目澄清（一對多）
   - `judge_languagelimit` 提供特定語言的時間/記憶體限制（一對多）
   - `judge_solution` 提供官方解答（一對一）

2. **多對多關係**：
   - 題目可以有多個作者、策展人、測試者
   - 題目可以屬於多種類型
   - 題目可以允許多種程式語言
   - 題目可以禁用特定使用者
   - 題目可以屬於多個組織

3. **Verilog 擴充功能**：
   - 支援波形處理和 PPA 計算
   - 整合 F4PGA 和 OpenLane 工具鏈
   - 提供 FPGA 和 ASIC 相關設定選項

此結構支援完整的題目管理功能，包括多語言、權限控制、Verilog 特色功能等。