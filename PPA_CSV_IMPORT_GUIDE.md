# DMOJ PPA CSV 匯入功能說明

## 📋 概述

DMOJ 支援通過 CSV 檔案批量匯入題目，並且完整支援 Verilog PPA（Performance, Power, Area）分析設定。

## 🔧 PPA 功能說明

### 基本設定

- **`enable_waveform`**: 啟用波形檢視功能 (true/false)
- **`enable_ppa`**: 啟用 PPA 分析功能 (true/false)

### 重要規則

1. **當 `enable_ppa=false` 時**：
   - 所有 F4PGA 和 OpenLane 相關欄位可以留空
   - 系統會自動將這些欄位設為空值
   - 不會產生資料庫錯誤

2. **當 `enable_ppa=true` 時**：
   - 可以選擇性設定 F4PGA 和/或 OpenLane 相關欄位
   - 至少需要設定其中一種分析方式

## 🔵 F4PGA FPGA 設定

用於 FPGA 合成和實現分析：

| 欄位 | 說明 | 範例值 |
|------|------|---------|
| `f4pga_board` | 目標 FPGA 開發板 | `basys3`, `arty_a7_100t` |
| `f4pga_target_fmax` | 目標最大頻率 (MHz) | `100.0`, `150.0` |

### 支援的開發板

- `basys3` - Digilent Basys3 (Artix-7)
- `arty_a7_35t` - Digilent Arty A7-35T
- `arty_a7_100t` - Digilent Arty A7-100T
- `nexys4_ddr` - Digilent Nexys 4 DDR
- `nexys_video` - Digilent Nexys Video
- `zybo_z7` - Digilent Zybo Z7

## 🟣 OpenLane ASIC 設定

用於 ASIC 設計和 PPA 分析：

| 欄位 | 說明 | 範例值 |
|------|------|---------|
| `openlane_pdk` | 製程設計套件 | `sky130A`, `sky130B` |
| `openlane_ppa_score` | 目標 PPA 分數 | `80.0`, `85.0` |
| `openlane_critical_path_ns` | 最大關鍵路徑延遲 (ns) | `5.0`, `3.5` |
| `openlane_core_area_um2` | 最大核心面積 (μm²) | `1000.0`, `800.0` |
| `openlane_power_total` | 最大總功耗 (mW) | `50.0`, `40.0` |

### 支援的 PDK

- `sky130A` - SkyWater 130nm PDK (Version A)
- `sky130B` - SkyWater 130nm PDK (Version B)
- `gf180mcuC` - GlobalFoundries 180nm MCU PDK (Version C)

## 📝 CSV 範例

### 1. 基本題目（無 PPA）

```csv
code,name,description,group,time_limit,memory_limit,points,...,enable_waveform,enable_ppa,f4pga_board,f4pga_target_fmax,openlane_pdk,openlane_ppa_score,openlane_critical_path_ns,openlane_core_area_um2,openlane_power_total,...
basic_hello,Hello World,基本輸出題目,Demo,1.0,262144,100,...,false,false,,,,,,,,...
```

### 2. 僅波形檢視

```csv
code,name,description,group,time_limit,memory_limit,points,...,enable_waveform,enable_ppa,f4pga_board,f4pga_target_fmax,openlane_pdk,openlane_ppa_score,openlane_critical_path_ns,openlane_core_area_um2,openlane_power_total,...
waveform_test,波形測試,檢視波形變化,Demo,2.0,262144,150,...,true,false,,,,,,,,...
```

### 3. F4PGA FPGA 分析

```csv
code,name,description,group,time_limit,memory_limit,points,...,enable_waveform,enable_ppa,f4pga_board,f4pga_target_fmax,openlane_pdk,openlane_ppa_score,openlane_critical_path_ns,openlane_core_area_um2,openlane_power_total,...
fpga_design,FPGA設計,FPGA合成測試,Demo,3.0,524288,250,...,true,true,basys3,100.0,,,,,...
```

### 4. OpenLane ASIC 分析

```csv
code,name,description,group,time_limit,memory_limit,points,...,enable_waveform,enable_ppa,f4pga_board,f4pga_target_fmax,openlane_pdk,openlane_ppa_score,openlane_critical_path_ns,openlane_core_area_um2,openlane_power_total,...
asic_design,ASIC設計,ASIC PPA測試,Demo,5.0,1048576,500,...,true,true,,,sky130A,80.0,5.0,1000.0,50.0,...
```

### 5. 混合 PPA 分析

```csv
code,name,description,group,time_limit,memory_limit,points,...,enable_waveform,enable_ppa,f4pga_board,f4pga_target_fmax,openlane_pdk,openlane_ppa_score,openlane_critical_path_ns,openlane_core_area_um2,openlane_power_total,...
mixed_design,混合設計,FPGA+ASIC分析,Demo,4.0,1048576,400,...,true,true,arty_a7_100t,150.0,sky130B,85.0,3.5,800.0,40.0,...
```

## ⚠️ 注意事項

1. **CSV 編碼**：請使用 UTF-8 編碼保存
2. **空值處理**：當 `enable_ppa=false` 時，PPA 相關欄位可以完全留空
3. **數值格式**：頻率、分數等數值使用小數點格式（如 `100.0`）
4. **布林值**：使用 `true`/`false`、`1`/`0` 或 `yes`/`no`
5. **逗號處理**：如果內容包含逗號，請用雙引號包圍

## 🔍 驗證規則

系統會進行以下驗證：

1. **必要欄位檢查**：確保所有必要欄位都有值
2. **開發板驗證**：檢查 F4PGA 開發板是否在支援清單中
3. **PDK 驗證**：檢查 OpenLane PDK 是否有效
4. **數值範圍檢查**：確保頻率、分數等數值在合理範圍內
5. **依賴關係檢查**：當 `enable_ppa=false` 時，忽略 PPA 相關欄位驗證

## 📄 下載範例

在 DMOJ 管理介面的 "匯入題目 CSV" 頁面，點擊 "下載範例 CSV" 按鈕可獲得包含各種 PPA 設定的完整範例檔案。
