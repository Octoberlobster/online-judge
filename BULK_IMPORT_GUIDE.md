# DMOJ 題目批量匯入腳本使用指南

## 📋 概述

`bulk_import_problems.py` 是一個專為 DMOJ 平台設計的題目批量匯入工具，支援從 CSV 檔案匯入完整的題目資料，包括 Verilog 特色功能、多語言翻譯、解答內容等。

## 🚀 快速開始

### 基本使用
```bash
python bulk_import_problems.py --csv enhanced_sample_problems.csv
```

### 更新現有題目
```bash
python bulk_import_problems.py --csv problems.csv --update --verbose
```

### 預演模式（測試用）
```bash
python bulk_import_problems.py --csv problems.csv --dry-run --verbose
```

## 📊 CSV 格式規範

### 必填欄位
| 欄位名稱 | 類型 | 說明 | 範例 |
|---------|------|------|------|
| `code` | 字串 | 題目代碼（唯一識別） | `hello_world` |
| `name` | 字串 | 題目名稱 | `Hello World` |
| `description` | 文字 | 題目描述 | `輸出 Hello World` |

### 基本設定欄位
| 欄位名稱 | 類型 | 預設值 | 說明 |
|---------|------|--------|------|
| `group` | 字串 | `Uncategorized` | 題目群組 |
| `time_limit` | 浮點數 | `1.0` | 時間限制（秒） |
| `memory_limit` | 整數 | `262144` | 記憶體限制（KB） |
| `points` | 浮點數 | `100` | 題目分數 |
| `is_public` | 布林 | `false` | 是否公開 |
| `partial` | 布林 | `false` | 允許部分分數 |
| `short_circuit` | 布林 | `false` | 短路評判 |
| `is_manually_managed` | 布林 | `false` | 手動管理 |

### Verilog 特色功能欄位
| 欄位名稱 | 類型 | 說明 |
|---------|------|------|
| `enable_waveform` | 布林 | 啟用波形圖處理 |
| `enable_ppa` | 布林 | 啟用 PPA 計算 |
| `ppa_maximum_fmax` | 浮點數 | 最大 Fmax 頻率 (MHz) |

#### F4PGA 設定
| 欄位名稱 | 類型 | 有效值 | 說明 |
|---------|------|--------|------|
| `f4pga_board` | 字串 | `basys3`, `arty_a7_35t`, `arty_a7_100t`, `nexys4_ddr`, `nexys_video`, `zybo_z7` | 目標開發板 |
| `f4pga_target_fmax` | 浮點數 | > 0.1 | 目標頻率 (MHz) |

#### OpenLane 設定
| 欄位名稱 | 類型 | 有效值 | 說明 |
|---------|------|--------|------|
| `openlane_pdk` | 字串 | `sky130A`, `sky130B`, `gf180mcuC` | PDK 選擇 |
| `openlane_ppa_score` | 浮點數 | >= 0 | 目標 PPA 分數 |
| `openlane_critical_path_ns` | 浮點數 | >= 0 | 最大關鍵路徑延遲 |
| `openlane_core_area_um2` | 浮點數 | >= 0 | 最大核心面積 |
| `openlane_power_total` | 浮點數 | >= 0 | 最大總功耗 |

### 關聯資料欄位
| 欄位名稱 | 格式 | 說明 | 範例 |
|---------|------|------|------|
| `types` | 逗號分隔 | 題目類型 | `Traditional,Math` |
| `authors` | 逗號分隔 | 作者使用者名稱 | `admin,teacher` |
| `curators` | 逗號分隔 | 策展人使用者名稱 | `curator1,curator2` |
| `testers` | 逗號分隔 | 測試者使用者名稱 | `tester1,tester2` |
| `allowed_languages` | 逗號分隔 | 允許的語言代碼 | `VLOG,PY3` |
| `organizations` | 逗號分隔 | 組織名稱 | `DMOJ,NUK` |
| `banned_users` | 逗號分隔 | 禁止使用者 | `banned1,banned2` |

### 其他功能欄位
| 欄位名稱 | 格式 | 說明 | 範例 |
|---------|------|------|------|
| `language_limits` | 管道分隔 | 語言限制 | `VLOG:2.0:524288\|PY3:1.0:262144` |
| `license` | 字串 | 授權許可代碼 | `CC0-1.0` |
| `og_image` | URL | OpenGraph 圖片 | `https://example.com/image.jpg` |
| `summary` | 字串 | 題目摘要 | `基礎邏輯閘練習` |

## 🔧 命令列選項

### 必要參數
- `--csv FILE`: 指定 CSV 檔案路徑

### 可選參數
- `--verbose, -v`: 顯示詳細輸出
- `--dry-run`: 預演模式，不實際修改資料庫
- `--update`: 更新已存在的題目（預設跳過）

## 📝 使用範例

### 1. 基本匯入
```bash
python bulk_import_problems.py --csv problems.csv
```

### 2. 詳細輸出模式
```bash
python bulk_import_problems.py --csv problems.csv --verbose
```

### 3. 預演測試
```bash
python bulk_import_problems.py --csv problems.csv --dry-run --verbose
```

### 4. 更新現有題目
```bash
python bulk_import_problems.py --csv problems.csv --update --verbose
```

## ⚠️ 注意事項

### 資料驗證
1. **題目代碼**: 必須是唯一的，只能包含小寫字母和數字
2. **群組和類型**: 必須在系統中已存在
3. **使用者**: 所有引用的使用者必須已註冊
4. **語言**: 必須在系統中已設定
5. **組織**: 必須在系統中已建立

### Verilog 特色功能
- 只有當 `enable_ppa=true` 時，PPA 相關欄位才會生效
- F4PGA 需要同時設定開發板和目標頻率
- OpenLane 設定為可選，可以只設定部分指標

### 翻譯系統
- 支援多種語言代碼：`en`, `zh-hant`, `zh-hans`, `ja`, `ko`, `es`, `fr`, `de`, `ru`
- 翻譯內容可以為空，但至少需要標題或描述其中一個
- 更新模式會清除現有翻譯後重新建立

### 錯誤處理
- 腳本會跳過有錯誤的行，繼續處理其他行
- 使用事務確保資料一致性
- 提供詳細的錯誤訊息和行號

## 🎯 CSV 範例檔案

請參考 `enhanced_sample_problems.csv` 檔案，其中包含了各種功能的完整範例。

## 📈 匯入結果

腳本會在結束時顯示匯入摘要：
```
==================================================
匯入結果摘要
==================================================
總計處理: 4 筆
成功創建: 3 筆
成功更新: 1 筆
跳過: 0 筆
錯誤: 0 筆
==================================================
```

## 🐛 常見問題

### Q: 題目代碼重複怎麼辦？
A: 預設會跳過重複的題目，使用 `--update` 參數可以更新現有題目。

### Q: 如何測試 CSV 格式是否正確？
A: 使用 `--dry-run` 參數進行預演，不會實際修改資料庫。

### Q: 支援哪些字元編碼？
A: 支援 UTF-8 和 UTF-8-BOM 編碼。

### Q: 如何處理大量題目匯入？
A: 腳本支援事務處理，可以安全地處理大量資料。建議先使用預演模式測試。

---

如有其他問題，請檢查詳細輸出（`--verbose`）或聯繫系統管理員。