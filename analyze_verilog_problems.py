#!/usr/bin/env python3
"""
分析 Verilog 問題 CSV 檔案中的語言使用情況
"""
import os
import sys
import django
import csv
import io

# 設定Django環境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')
django.setup()

from judge.models import Language

def analyze_csv_content(csv_content):
    """分析 CSV 內容中的語言使用情況"""
    languages_found = set()
    translations_found = set()
    
    # 解析 CSV
    csv_reader = csv.DictReader(io.StringIO(csv_content))
    
    problem_count = 0
    for row in csv_reader:
        problem_count += 1
        
        # 檢查 allowed_languages 欄位
        allowed_langs = row.get('allowed_languages', '').strip()
        if allowed_langs:
            lang_keys = [lang.strip() for lang in allowed_langs.split(',')]
            languages_found.update(lang_keys)
        
        # 檢查 translations 欄位中的語言代碼
        translations = row.get('translations', '').strip()
        if translations:
            # 解析翻譯格式: lang:title:description|lang:title:description
            for translation in translations.split('|'):
                if ':' in translation:
                    lang_code = translation.split(':')[0].strip()
                    translations_found.add(lang_code)
        
        # 檢查 language_limits 欄位
        lang_limits = row.get('language_limits', '').strip()
        if lang_limits:
            # 解析語言限制格式: LANG:time:memory|LANG:time:memory
            for limit in lang_limits.split('|'):
                if ':' in limit:
                    lang_code = limit.split(':')[0].strip()
                    languages_found.add(lang_code)
    
    return {
        'problem_count': problem_count,
        'programming_languages': languages_found,
        'translation_languages': translations_found
    }

def check_database_languages():
    """檢查資料庫中現有的語言"""
    db_languages = {}
    for lang in Language.objects.all():
        db_languages[lang.key] = lang.name
    
    return db_languages

# 請將 CSV 檔案內容貼在這裡進行分析
print("請提供 CSV 檔案內容進行分析...")