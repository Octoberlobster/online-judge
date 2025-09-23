#!/usr/bin/env python3
"""
修改 CSV 檔案，只保留指定的翻譯語言
"""
import csv
import io

def filter_translations(csv_content, wanted_languages=['en', 'zh-hant']):
    """
    過濾翻譯，只保留指定的語言
    
    Args:
        csv_content: CSV 檔案內容
        wanted_languages: 想要保留的語言代碼列表
    """
    lines = csv_content.strip().split('\n')
    if not lines:
        return csv_content
    
    # 解析標題行
    header = lines[0]
    result_lines = [header]
    
    # 處理每一行數據
    csv_reader = csv.DictReader(io.StringIO(csv_content))
    fieldnames = csv_reader.fieldnames
    
    filtered_rows = []
    for row in csv_reader:
        # 處理翻譯欄位
        translations = row.get('translations', '').strip()
        if translations:
            filtered_translations = []
            for translation in translations.split('|'):
                translation = translation.strip()
                if translation and ':' in translation:
                    lang_code = translation.split(':')[0].strip()
                    if lang_code in wanted_languages:
                        filtered_translations.append(translation)
            row['translations'] = '|'.join(filtered_translations)
        
        # 處理澄清說明欄位
        clarifications = row.get('clarifications', '').strip()
        if clarifications:
            filtered_clarifications = []
            for clarification in clarifications.split('|'):
                clarification = clarification.strip()
                if clarification and ':' in clarification:
                    lang_code = clarification.split(':')[0].strip()
                    if lang_code in wanted_languages:
                        filtered_clarifications.append(clarification)
            row['clarifications'] = '|'.join(filtered_clarifications)
        
        filtered_rows.append(row)
    
    # 重新組成 CSV
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(filtered_rows)
    
    return output.getvalue()

# 使用範例
print("CSV 翻譯語言過濾工具")
print("=" * 40)
print("功能：將 CSV 檔案中的翻譯語言過濾，只保留指定的語言")
print()
print("支援的語言代碼：")
print("- en: 英文")
print("- zh-hant: 繁體中文") 
print("- zh-hans: 簡體中文")
print("- ja: 日文")
print("- ko: 韓文")
print()
print("請提供 CSV 內容進行處理...")