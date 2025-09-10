# 快速 CSV 匯入指南

## 🚀 立即使用

### 1. 準備工作
確保您的系統中存在：
- 題目群組 `test`（或修改 CSV 中的 group 欄位）
- Verilog 語言支援

### 2. 選擇檔案
- **簡化版**: `simple_import.csv` - 只包含核心欄位，4個範例題目
- **完整版**: `web_import_sample.csv` - 包含所有欄位，展示更多功能

### 3. 匯入步驟
1. 登入管理介面：`http://your-domain/admin/`
2. 進入 Judge → Problems
3. 點選右上角 "匯入 CSV"
4. 上傳檔案，點選 "預覽"
5. 確認無誤後點選 "匯入"

## 📋 範例題目說明

### simple_import.csv 包含：

1. **logic01** - 基本邏輯閘
   - 只啟用波形檢視
   - 適合初學者

2. **fpga01** - FPGA 計數器  
   - 啟用 F4PGA (Basys3)
   - 中等難度

3. **asic01** - 簡單 ALU
   - 啟用 OpenLane (sky130A)
   - 包含 PPA 目標

4. **cpu01** - RISC-V 核心
   - 同時啟用 F4PGA + OpenLane
   - 高級設計挑戰

## ⚙️ 快速自訂

### 修改題目群組
```csv
# 將 group 欄位改為您的群組名稱
code,name,description,group,...
mycode,我的題目,描述,my_group,...
```

### 調整 PPA 設定
```csv
# enable_ppa=false: 只顯示波形
# enable_ppa=true: 顯示 F4PGA/OpenLane 設定
enable_ppa,f4pga_board,openlane_pdk
false,,,
true,basys3,,
true,,sky130A,
true,arty_a7_100t,sky130B
```

### F4PGA 開發板選項
- `basys3` - Basys3 (入門)
- `arty_a7_35t` - Arty A7-35T 
- `arty_a7_100t` - Arty A7-100T (推薦)
- `nexys4_ddr` - Nexys 4 DDR
- `nexys_video` - Nexys Video
- `zybo_z7` - Zybo Z7

### OpenLane PDK 選項  
- `sky130A` - SkyWater 130nm (穩定)
- `sky130B` - SkyWater 130nm (新版)
- `gf180mcuC` - GlobalFoundries 180nm

## 🔧 故障排除

### 常見錯誤
1. **群組不存在** → 先建立群組或修改 CSV
2. **語言不存在** → 確保已註冊 Verilog 語言
3. **編碼問題** → 確保檔案為 UTF-8 編碼
4. **題目代碼重複** → 修改 code 欄位確保唯一

### 檢查步驟
1. 預覽功能是您的好朋友
2. 從簡單範例開始
3. 逐步添加複雜設定
4. 檢查瀏覽器控制台錯誤

## 📞 需要協助？

如果遇到問題，請檢查：
1. Django 日誌中的錯誤訊息
2. 瀏覽器開發者工具
3. 資料庫中是否有必要的參考資料

範例檔案已經過測試，應該可以直接使用！
