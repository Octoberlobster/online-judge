# DMOJ 題目描述處理指南

## 🎯 目標
設計最佳的 CSV 格式來正確儲存和解析題目描述，確保：
1. 字符編碼正確處理
2. Markdown 格式完整保存
3. 多語言支援
4. 禁用字符自動清理
5. 網頁顯示正確

## 📊 資料庫描述儲存分析

### 核心欄位結構
```sql
-- 主要題目描述
Problem.description (TextField, 支援 Markdown)
  - 驗證器: disallowed_characters_validator
  - 禁用字符: {'"', '"', ''', ''', '−', 'ﬀ', 'ﬁ', 'ﬂ', 'ﬃ', 'ﬄ'}
  - 支援完整 Markdown 語法

-- 多語言翻譯
ProblemTranslation.description (TextField)
  - 相同的字符驗證器
  - 語言代碼: en, zh-hans, zh-hant 等

-- 澄清說明
ProblemClarification.description (TextField)
  - 相同的字符驗證器
  - 時間戳記錄
```

### 字符處理規則
```python
# 禁用字符替換映射
CHAR_REPLACEMENTS = {
    '"': '"',    # 左雙引號 → 標準雙引號
    '"': '"',    # 右雙引號 → 標準雙引號  
    ''': "'",    # 左單引號 → 標準單引號
    ''': "'",    # 右單引號 → 標準單引號
    '−': '-',    # 數學減號 → 連字符
    'ﬀ': 'ff',   # 連字符 ff
    'ﬁ': 'fi',   # 連字符 fi
    'ﬂ': 'fl',   # 連字符 fl
    'ﬃ': 'ffi',  # 連字符 ffi
    'ﬄ': 'ffl',  # 連字符 ffl
}
```

## 🚀 增強 CSV 格式設計

### 基本描述欄位
```csv
code,name,description,description_format,is_full_markup
```

### 多語言支援欄位
```csv
code,name,description,
translation_en_name,translation_en_description,
translation_zh_name,translation_zh_description,
translation_zh_hant_name,translation_zh_hant_description
```

### 完整增強格式
```csv
code,name,description,description_format,is_full_markup,group,time_limit,memory_limit,points,
translation_en_name,translation_en_description,
translation_zh_name,translation_zh_description,
translation_zh_hant_name,translation_zh_hant_description,
clarifications,allowed_languages,is_public
```

## 📝 CSV 內容處理規範

### 1. 描述內容格式化
```csv
# 基本 Markdown 支援
description,description_format
"# 題目標題

這是一個**重要**的題目。

## 輸入格式
- 第一行：整數 n
- 第二行：n 個整數

## 輸出格式
輸出一個整數

## 範例
```
輸入:
3
1 2 3

輸出:
6
```

## 限制
- 1 ≤ n ≤ 1000
",markdown
```

### 2. 多語言描述
```csv
code,name,description,translation_en_name,translation_en_description,translation_zh_hant_name,translation_zh_hant_description
hello_world,"Hello World","輸出 Hello World","Hello World","Output Hello World","哈囉世界","輸出哈囉世界"
```

### 3. 特殊字符處理
```csv
# CSV 中的特殊字符轉義
description
"這是包含""引號""的描述\n這是新的一行\n\n這是空行後的內容"
```

### 4. 長文本折行
```csv
# 長描述可以使用反斜線折行
description
"這是一個很長的描述，\
可以使用反斜線來\
分行書寫，\
提高可讀性"
```

## 🛠 CSV 處理工具

### 自動字符清理
```python
def clean_description(text):
    """自動清理和標準化描述文字"""
    # 1. 替換禁用字符
    for old_char, new_char in CHAR_REPLACEMENTS.items():
        text = text.replace(old_char, new_char)
    
    # 2. 標準化換行符
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # 3. 處理多餘空白
    lines = [line.rstrip() for line in text.split('\n')]
    
    # 4. 限制連續空行
    result = []
    empty_count = 0
    for line in lines:
        if not line.strip():
            empty_count += 1
            if empty_count <= 2:
                result.append(line)
        else:
            empty_count = 0
            result.append(line)
    
    return '\n'.join(result).strip()
```

### Markdown 驗證
```python
def validate_markdown(text):
    """驗證 Markdown 格式"""
    # 檢查常見 Markdown 語法錯誤
    issues = []
    
    # 檢查程式碼區塊
    if text.count('```') % 2 != 0:
        issues.append("程式碼區塊標記不匹配")
    
    # 檢查表格格式
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if '|' in line and i + 1 < len(lines):
            next_line = lines[i + 1]
            if set(next_line.replace(' ', '')) <= {'|', '-', ':'}:
                # 這是表格標題行
                if line.count('|') != next_line.count('|'):
                    issues.append(f"第 {i+1} 行表格格式錯誤")
    
    return issues
```

## 📋 範例 CSV 檔案

### 基本範例
```csv
code,name,description,group,time_limit,memory_limit,points,is_public
aplusb,"A+B Problem","# A+B Problem

給定兩個整數 a 和 b，計算它們的和。

## 輸入格式
一行包含兩個整數 a 和 b。

## 輸出格式
輸出一個整數，即 a + b 的結果。

## 範例
```
輸入: 1 2
輸出: 3
```

## 限制
- -1000 ≤ a, b ≤ 1000
",Demo,1.0,65536,100,true
```

### 多語言範例
```csv
code,name,description,translation_en_name,translation_en_description,group,time_limit,memory_limit,points,is_public
fibonacci,"費氏數列","# 費氏數列

計算第 n 個費氏數列項。

費氏數列定義：
- F(0) = 0
- F(1) = 1  
- F(n) = F(n-1) + F(n-2)

## 輸入格式
一個整數 n (0 ≤ n ≤ 30)

## 輸出格式
第 n 個費氏數列項

## 範例
```
輸入: 5
輸出: 5
```
","Fibonacci Sequence","# Fibonacci Sequence

Calculate the nth Fibonacci number.

The Fibonacci sequence is defined as:
- F(0) = 0
- F(1) = 1
- F(n) = F(n-1) + F(n-2)

## Input Format
One integer n (0 ≤ n ≤ 30)

## Output Format
The nth Fibonacci number

## Example
```
Input: 5
Output: 5
```
",Math,2.0,65536,150,true
```

### Verilog 專用範例
```csv
code,name,description,group,time_limit,memory_limit,points,allowed_languages,enable_waveform,enable_ppa,f4pga_board,f4pga_target_fmax,is_public
verilog_counter,"8位元計數器","# 8位元二進制計數器

設計一個8位元的二進制計數器模組。

## 模組介面
```verilog
module counter_8bit(
    input clk,
    input reset,
    output [7:0] count
);
```

## 功能要求
1. 時鐘上升緣觸發計數
2. reset 高電平時重置為 0
3. 計數範圍：0 到 255
4. 溢出後回到 0

## 時序要求
- 最大頻率：100 MHz
- 重置延遲：1 個時鐘週期

## 測試案例
1. 基本計數功能
2. 重置功能
3. 溢出處理
4. 時序分析

## 評分標準
- 功能正確性：70%
- 時序性能：20%
- 資源利用：10%
",Demo,3.0,262144,200,Verilog,true,true,basys3,100.0,true
```

## ⚠️ 注意事項

### 編碼要求
- **必須使用 UTF-8 with BOM** 編碼保存 CSV
- Excel 可能會改變編碼，建議使用文字編輯器
- 上傳前檢查檔案編碼

### 特殊字符處理
- 避免使用禁用字符集中的字符
- 使用標準 ASCII 引號和標點符號
- 程式碼區塊中的特殊字符會自動處理

### 長文本建議
- 複雜題目建議拆分為多個段落
- 使用 Markdown 標題結構化內容
- 表格和程式碼區塊需要特別注意格式

### 多語言注意
- 語言代碼必須與系統設定一致
- 翻譯內容應保持結構相同
- 程式碼範例可以保持相同

## 🔧 自動化工具

使用 `enhanced_description_import.py` 進行描述處理：

```bash
# 試運行檢查
python enhanced_description_import.py --csv problems.csv --dry-run --verbose

# 實際匯入
python enhanced_description_import.py --csv problems.csv --verbose
```

這個工具會自動：
1. 清理禁用字符
2. 驗證 Markdown 格式
3. 處理多語言翻譯
4. 報告處理統計