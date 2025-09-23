#!/usr/bin/env python3
"""
分析 CSV 檔案中的翻譯語言
"""
import csv
import io

def analyze_translation_languages(csv_content):
    """分析 CSV 內容中的翻譯語言"""
    translation_languages = set()
    clarification_languages = set()
    problems_with_translations = 0
    total_problems = 0
    
    # 解析 CSV
    csv_reader = csv.DictReader(io.StringIO(csv_content))
    
    for row in csv_reader:
        total_problems += 1
        
        # 檢查 translations 欄位
        translations = row.get('translations', '').strip()
        if translations:
            problems_with_translations += 1
            # 解析翻譯格式: lang:title:description|lang:title:description
            for translation in translations.split('|'):
                if ':' in translation:
                    lang_code = translation.split(':')[0].strip()
                    translation_languages.add(lang_code)
        
        # 檢查 clarifications 欄位
        clarifications = row.get('clarifications', '').strip()
        if clarifications:
            # 解析澄清說明格式: lang:question:answer|lang:question:answer
            for clarification in clarifications.split('|'):
                if ':' in clarification:
                    lang_code = clarification.split(':')[0].strip()
                    clarification_languages.add(lang_code)
    
    return {
        'total_problems': total_problems,
        'problems_with_translations': problems_with_translations,
        'translation_languages': sorted(translation_languages),
        'clarification_languages': sorted(clarification_languages),
        'all_languages': sorted(translation_languages | clarification_languages)
    }

# 語言代碼對應表
language_names = {
    'en': '英文 (English)',
    'zh': '中文 (Chinese)',
    'zh-cn': '簡體中文 (Simplified Chinese)',
    'zh-tw': '繁體中文 (Traditional Chinese)',
    'zh-hant': '繁體中文 (Traditional Chinese)',
    'zh-hans': '簡體中文 (Simplified Chinese)',
    'ja': '日文 (Japanese)',
    'ko': '韓文 (Korean)',
    'fr': '法文 (French)',
    'de': '德文 (German)',
    'es': '西班牙文 (Spanish)',
    'pt': '葡萄牙文 (Portuguese)',
    'ru': '俄文 (Russian)',
    'it': '義大利文 (Italian)',
    'ar': '阿拉伯文 (Arabic)',
}

def get_language_name(code):
    """獲取語言代碼對應的中文名稱"""
    return language_names.get(code, f'未知語言 ({code})')

print("請將 CSV 檔案內容貼上，我會分析其中的翻譯語言...")
print("=" * 60)