#!/usr/bin/env python
"""
DMOJ 增強題目描述匯入工具

專門處理題目描述的正確編碼、Markdown 格式化和多語言支援

主要功能：
1. 自動清理禁用字符
2. Markdown 格式驗證和轉換
3. 多語言描述支援
4. 描述內容編碼處理
5. 長文本折行處理

使用方法：
    python enhanced_description_import.py --csv enhanced_descriptions.csv
"""

import os
import sys
import csv
import re
import argparse
import django
from typing import Dict, List, Any, Optional

# 設定 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')
django.setup()

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
from judge.models import Problem, ProblemTranslation
from judge.models.problem import disallowed_characters_validator


class DescriptionProcessor:
    """題目描述處理器"""
    
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.disallowed_chars = getattr(settings, 'DMOJ_PROBLEM_STATEMENT_DISALLOWED_CHARACTERS', set())
        
    def clean_disallowed_characters(self, text: str) -> str:
        """清理禁用字符"""
        if not text:
            return text
            
        # 替換禁用字符為標準字符
        char_replacements = {
            '"': '"',   # 左雙引號 → 標準雙引號
            '"': '"',   # 右雙引號 → 標準雙引號
            ''': "'",   # 左單引號 → 標準單引號
            ''': "'",   # 右單引號 → 標準單引號
            '−': '-',   # 數學減號 → 連字符
            'ﬀ': 'ff', # 連字符 ff
            'ﬁ': 'fi', # 連字符 fi
            'ﬂ': 'fl', # 連字符 fl
            'ﬃ': 'ffi', # 連字符 ffi
            'ﬄ': 'ffl', # 連字符 ffl
        }
        
        cleaned_text = text
        for disallowed_char, replacement in char_replacements.items():
            if disallowed_char in self.disallowed_chars:
                cleaned_text = cleaned_text.replace(disallowed_char, replacement)
                
        return cleaned_text
    
    def process_markdown_content(self, content: str) -> str:
        """處理 Markdown 內容"""
        if not content:
            return content
            
        # 1. 清理禁用字符
        content = self.clean_disallowed_characters(content)
        
        # 2. 標準化換行符
        content = content.replace('\r\n', '\n').replace('\r', '\n')
        
        # 3. 處理多餘空白
        lines = content.split('\n')
        processed_lines = []
        
        for line in lines:
            # 移除行尾空白，但保留行首縮排
            line = line.rstrip()
            processed_lines.append(line)
        
        # 4. 合併空行（最多保留兩個連續空行）
        result_lines = []
        empty_line_count = 0
        
        for line in processed_lines:
            if not line.strip():
                empty_line_count += 1
                if empty_line_count <= 2:
                    result_lines.append(line)
            else:
                empty_line_count = 0
                result_lines.append(line)
        
        return '\n'.join(result_lines).strip()
    
    def validate_description(self, description: str) -> bool:
        """驗證描述內容"""
        try:
            disallowed_characters_validator(description)
            return True
        except ValidationError as e:
            if self.verbose:
                print(f"描述驗證失敗: {e}")
            return False
    
    def process_csv_description(self, description_text: str, preserve_formatting: bool = True) -> str:
        """處理 CSV 中的描述文字"""
        if not description_text:
            return ""
        
        # 處理 CSV 中的轉義字符
        # 還原 CSV 轉義的換行符
        description_text = description_text.replace('\\n', '\n')
        description_text = description_text.replace('\\r', '\r')
        description_text = description_text.replace('\\t', '\t')
        description_text = description_text.replace('\\"', '"')
        description_text = description_text.replace("\\'", "'")
        
        if preserve_formatting:
            return self.process_markdown_content(description_text)
        else:
            # 簡單清理模式
            return self.clean_disallowed_characters(description_text.strip())
    
    def prepare_csv_output(self, description: str) -> str:
        """準備用於 CSV 輸出的描述文字"""
        if not description:
            return ""
        
        # 轉義特殊字符以適合 CSV 格式
        escaped = description.replace('"', '""')  # CSV 雙引號轉義
        escaped = escaped.replace('\n', '\\n')    # 換行符轉義
        escaped = escaped.replace('\r', '\\r')    # 回車符轉義
        escaped = escaped.replace('\t', '\\t')    # Tab 轉義
        
        return escaped


class EnhancedProblemImporter:
    """增強的題目匯入器，專注於描述處理"""
    
    def __init__(self, verbose=False, dry_run=False):
        self.verbose = verbose
        self.dry_run = dry_run
        self.description_processor = DescriptionProcessor(verbose)
        self.stats = {
            'total': 0,
            'processed': 0,
            'errors': 0,
            'cleaned_chars': 0
        }
    
    def import_from_csv(self, csv_file_path: str) -> Dict[str, int]:
        """從 CSV 匯入題目描述"""
        try:
            with open(csv_file_path, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                
                for row_num, row in enumerate(reader, start=2):
                    self.stats['total'] += 1
                    
                    try:
                        self.process_problem_row(row, row_num)
                        self.stats['processed'] += 1
                        
                    except Exception as e:
                        self.stats['errors'] += 1
                        print(f"行 {row_num} 處理錯誤: {e}")
                        
        except Exception as e:
            print(f"檔案讀取錯誤: {e}")
            
        return self.stats
    
    def process_problem_row(self, row: Dict[str, str], row_num: int):
        """處理單一題目行"""
        code = row.get('code', '').strip()
        if not code:
            raise ValueError("題目代碼不能為空")
        
        # 獲取現有題目或創建新題目標記
        try:
            problem = Problem.objects.get(code=code)
            is_new = False
        except Problem.DoesNotExist:
            problem = None
            is_new = True
        
        # 處理主要描述
        main_description = row.get('description', '')
        if main_description:
            processed_description = self.description_processor.process_csv_description(main_description)
            
            # 驗證描述
            if not self.description_processor.validate_description(processed_description):
                raise ValidationError(f"描述包含禁用字符")
            
            if self.verbose:
                print(f"題目 {code}: 描述處理完成 ({len(processed_description)} 字符)")
            
            # 更新或創建題目 (僅在非試運行模式)
            if not self.dry_run:
                if is_new:
                    # 這裡只處理描述，其他必要欄位需要在主匯入腳本中處理
                    print(f"新題目 {code} 需要完整的匯入流程")
                else:
                    problem.description = processed_description
                    problem.save(update_fields=['description'])
                    
        # 處理多語言翻譯
        self.process_translations(problem, row, code)
    
    def process_translations(self, problem, row: Dict[str, str], code: str):
        """處理多語言翻譯"""
        translation_fields = [
            ('translation_en_name', 'translation_en_description', 'en'),
            ('translation_zh_name', 'translation_zh_description', 'zh-hans'),
            ('translation_zh_hant_name', 'translation_zh_hant_description', 'zh-hant'),
        ]
        
        for name_field, desc_field, lang_code in translation_fields:
            name = row.get(name_field, '').strip()
            description = row.get(desc_field, '').strip()
            
            if name or description:
                if description:
                    processed_desc = self.description_processor.process_csv_description(description)
                    if not self.description_processor.validate_description(processed_desc):
                        print(f"警告: {code} 的 {lang_code} 翻譯描述包含禁用字符")
                        continue
                
                if not self.dry_run and problem:
                    translation, created = ProblemTranslation.objects.get_or_create(
                        problem=problem,
                        language=lang_code,
                        defaults={
                            'name': name or problem.name,
                            'description': processed_desc if description else problem.description
                        }
                    )
                    
                    if not created and (name or description):
                        if name:
                            translation.name = name
                        if description:
                            translation.description = processed_desc
                        translation.save()
                
                if self.verbose:
                    print(f"  翻譯 {lang_code}: {'新增' if (not problem or 'created' in locals()) else '更新'}")


def main():
    parser = argparse.ArgumentParser(description="DMOJ 增強題目描述匯入工具")
    parser.add_argument('--csv', required=True, help='CSV 檔案路徑')
    parser.add_argument('--dry-run', action='store_true', help='試運行模式，不實際修改資料庫')
    parser.add_argument('--verbose', '-v', action='store_true', help='詳細輸出')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.csv):
        print(f"錯誤: CSV 檔案 '{args.csv}' 不存在")
        sys.exit(1)
    
    importer = EnhancedProblemImporter(verbose=args.verbose, dry_run=args.dry_run)
    
    print(f"開始處理 CSV 檔案: {args.csv}")
    if args.dry_run:
        print("*** 試運行模式：不會修改資料庫 ***")
    
    stats = importer.import_from_csv(args.csv)
    
    print("\n=== 處理統計 ===")
    print(f"總行數: {stats['total']}")
    print(f"成功處理: {stats['processed']}")
    print(f"錯誤: {stats['errors']}")
    print(f"字符清理: {stats['cleaned_chars']}")


if __name__ == '__main__':
    main()