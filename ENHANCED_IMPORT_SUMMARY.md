# DMOJ 增強版 CSV 題目匯入系統 - 更新總結

## 概述

基於您提供的 `enhanced_sample_problems (1).csv` 格式，我已經創建了一套完整的題目批量匯入系統，完全對應到 DMOJ 資料庫的表結構。

## 📁 新增檔案

### 核心腳本
1. **`enhanced_bulk_import_problems.py`** (785 行)
   - 主要匯入腳本，支援所有 42 個 CSV 欄位
   - 完整的錯誤處理和日誌記錄
   - 試運行模式和跳過錯誤選項

2. **`test_enhanced_import.py`** (244 行)
   - 自動化測試腳本
   - 創建測試資料、執行匯入、驗證結果
   - 自動清理測試資料

### 範例和文檔
3. **`enhanced_sample_data.csv`**
   - 包含 3 個完整範例的 CSV 資料
   - 展示各種功能的使用方法

4. **`ENHANCED_BULK_IMPORT_GUIDE.md`** (詳細指南)
   - 完整的使用說明（42個欄位詳解）
   - 故障排除和最佳實踐
   - 安全注意事項

5. **`ENHANCED_QUICK_START.md`** (快速開始)
   - 快速上手指南
   - 新舊版本對比
   - 常見問題解答

### 更新檔案
6. **`enhanced_sample_problems (1).csv`** (已更新)
   - 添加中文欄位說明
   - 包含範例行註釋

## 🎯 主要功能特色

### 1. 完整的資料庫欄位支援 (42 個欄位)

#### 基本題目資訊
- `code`, `name`, `description`, `group`
- `time_limit`, `memory_limit`, `points`
- `is_public`, `partial`, `short_circuit`, `is_manually_managed`
- `license`, `og_image`, `summary`, `is_full_markup`

#### 關聯資料 (多對多關係)
- `types` - 題目類型
- `authors`, `curators`, `testers` - 人員關聯
- `allowed_languages` - 允許語言
- `banned_users` - 禁用使用者
- `organizations` - 組織關聯
- `is_organization_private` - 組織私有設定

#### Verilog/FPGA 特色功能
- `enable_waveform` - 波形圖處理
- `enable_ppa` - PPA 分析
- `ppa_maximum_fmax` - 最大頻率限制
- `f4pga_board`, `f4pga_target_fmax` - F4PGA 設定
- `openlane_pdk` - OpenLane PDK 選擇
- `openlane_ppa_score`, `openlane_critical_path_ns` - OpenLane 指標
- `openlane_core_area_um2`, `openlane_power_total` - 面積和功耗

#### 解答系統
- `solution_content` - 解答內容
- `solution_is_public` - 解答可見性
- `solution_authors` - 解答作者

#### 多語言翻譯
- `translation_en_name`, `translation_en_description` - 英文翻譯
- `translation_zh_hant_name`, `translation_zh_hant_description` - 繁體中文翻譯

#### 進階功能
- `clarifications` - 題目澄清 (分號分隔)
- `language_limits` - 語言特定限制 (格式：`lang:time:memory`)

### 2. 智能資料處理

#### 型別轉換
```python
# 布林值解析
'true', '1', 'yes', 'enabled', '是', '啟用' → True

# 數值解析
'3.14' → 3.14 (float)
'256' → 256 (int)
'' → None (空值處理)

# 列表解析
'type1,type2,type3' → ['type1', 'type2', 'type3']
'clarification1;clarification2' → ['clarification1', 'clarification2']
```

#### 關聯資料處理
```python
# 自動創建缺失的資料
- 題目群組 (ProblemGroup)
- 題目類型 (ProblemType)

# 智能查找現有資料
- 使用者檔案 (Profile)
- 程式語言 (Language)
- 組織 (Organization)
- 授權許可 (License)
```

### 3. 完整的錯誤處理

#### 驗證機制
- CSV 格式驗證
- 必填欄位檢查
- 資料型別驗證
- 關聯資料存在性檢查

#### 錯誤恢復
- `--skip-errors` 選項跳過錯誤繼續處理
- 詳細的錯誤日誌記錄
- 事務回滾機制保證資料一致性

### 4. 進階運行模式

#### 試運行模式
```bash
python enhanced_bulk_import_problems.py --csv data.csv --dry-run
```
- 驗證 CSV 格式和資料
- 不實際修改資料庫
- 輸出完整的處理摘要

#### 詳細日誌
```bash
python enhanced_bulk_import_problems.py --csv data.csv --log-level DEBUG
```
- 支援 DEBUG/INFO/WARNING/ERROR 等級
- 同時輸出到檔案和控制台
- 包含處理統計和錯誤追蹤

## 🗄️ 資料庫表結構對應

### 主要資料表
```sql
judge_problem (主題目表)
├── judge_problemtranslation (翻譯)
├── judge_solution (解答)
├── judge_problemclarification (澄清)
└── judge_languagelimit (語言限制)
```

### 關聯資料表
```sql
judge_problem_authors (作者關聯)
judge_problem_curators (策展人關聯)
judge_problem_testers (測試者關聯)
judge_problem_types (類型關聯)
judge_problem_allowed_languages (語言關聯)
judge_problem_banned_users (禁用使用者關聯)
judge_problem_organizations (組織關聯)
```

### Verilog 欄位支援
所有 Verilog/FPGA 相關欄位直接對應到 `judge_problem` 表：
- F4PGA 板卡選項：`basys3`, `arty_a7_35t`, `nexys4_ddr` 等
- OpenLane PDK 選項：`sky130A`, `sky130B`, `gf180mcuC`
- PPA 指標：面積、功耗、頻率、關鍵路徑

## 🚀 使用示例

### 1. 快速測試
```bash
# 運行自動化測試
python test_enhanced_import.py

# 使用範例資料測試
python enhanced_bulk_import_problems.py --csv enhanced_sample_data.csv --dry-run
```

### 2. 實際匯入
```bash
# 匯入你的 CSV 資料
python enhanced_bulk_import_problems.py --csv your_data.csv

# 跳過錯誤繼續處理
python enhanced_bulk_import_problems.py --csv your_data.csv --skip-errors
```

### 3. CSV 格式範例
```csv
code,name,description,group,time_limit,points,enable_waveform,f4pga_board
sample001,測試加法器,設計加法器電路,basic,2.0,5.0,true,basys3
```

## 📊 與原版本對比

| 特性 | 原版本 | 增強版本 |
|------|--------|----------|
| CSV 欄位數量 | ~15 個 | 42 個 |
| Verilog 支援 | 基本 | 完整 (10個專用欄位) |
| 翻譯支援 | ❌ | ✅ (英文+繁中) |
| 解答匯入 | ❌ | ✅ (內容+作者+可見性) |
| 澄清匯入 | ❌ | ✅ (批量匯入) |
| 語言限制 | ❌ | ✅ (個別設定) |
| 錯誤處理 | 基本 | 增強 (跳過+日誌) |
| 測試支援 | ❌ | ✅ (自動化測試) |
| 試運行 | ❌ | ✅ (--dry-run) |
| 文檔 | 簡單 | 完整 (3個指南) |

## 🔧 技術實現亮點

### 1. 模組化設計
```python
class EnhancedBulkImporter:
    def handle_many_to_many_relations()
    def handle_translations()
    def handle_solution()
    def handle_clarifications()
    def handle_language_limits()
```

### 2. 智能型別轉換
```python
def parse_boolean(self, value: str) -> bool
def parse_float(self, value: str) -> Optional[float]
def parse_list(self, value: str, separator: str = ',') -> List[str]
```

### 3. 事務安全
```python
with transaction.atomic():
    # 所有資料庫操作在事務中進行
    # 失敗時自動回滾
```

### 4. 容錯機制
```python
try:
    # 處理題目
except Exception as e:
    if self.skip_errors:
        logger.error(f"跳過錯誤: {e}")
        continue
    else:
        raise
```

## 📋 下一步建議

### 1. 立即可用
- 所有檔案已準備完成
- 執行權限已設定
- 可直接使用 `test_enhanced_import.py` 驗證

### 2. 生產環境部署
1. 備份現有資料庫
2. 使用 `--dry-run` 驗證 CSV 格式
3. 小批量測試匯入
4. 監控日誌檔案

### 3. 自訂擴展
- 可輕鬆添加新的 CSV 欄位
- 支援自訂資料驗證規則
- 可擴展至其他匯入格式

## 🎉 總結

這套增強版題目匯入系統提供了：
- **完整性**: 支援所有 42 個 CSV 欄位
- **穩定性**: 完整的錯誤處理和事務安全
- **易用性**: 詳細文檔和自動化測試
- **靈活性**: 多種運行模式和選項
- **擴展性**: 模組化設計便於維護

系統已完全準備就緒，可以立即投入使用！