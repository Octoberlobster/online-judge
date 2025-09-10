#!/usr/bin/env python3
"""
分析 Problem 模型的必填欄位
"""
import os
import sys
import django

# 設定 Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')
sys.path.append('/home/xc/dmoj-site')
django.setup()

from judge.models import Problem
from django.db import models

def analyze_problem_fields():
    """分析 Problem 模型的欄位"""
    print("Problem 模型欄位分析")
    print("=" * 80)
    
    required_fields = []
    optional_fields = []
    foreign_key_fields = []
    many_to_many_fields = []
    
    for field in Problem._meta.get_fields():
        field_name = field.name
        field_type = type(field).__name__
        
        info = {
            'name': field_name,
            'type': field_type,
            'required': False,
            'default': None,
            'help_text': getattr(field, 'help_text', ''),
            'choices': getattr(field, 'choices', None)
        }
        
        # 檢查是否為必填欄位
        if hasattr(field, 'null') and hasattr(field, 'blank'):
            if not field.null and not field.blank:
                if not hasattr(field, 'default') or field.default == models.NOT_PROVIDED:
                    info['required'] = True
        elif hasattr(field, 'blank'):
            if not field.blank:
                if not hasattr(field, 'default') or field.default == models.NOT_PROVIDED:
                    info['required'] = True
        
        # 取得預設值
        if hasattr(field, 'default') and field.default != models.NOT_PROVIDED:
            info['default'] = field.default
            
        # 分類欄位
        if field_type == 'ForeignKey':
            foreign_key_fields.append(info)
        elif field_type == 'ManyToManyField':
            many_to_many_fields.append(info)
        elif info['required']:
            required_fields.append(info)
        else:
            optional_fields.append(info)
    
    # 顯示必填欄位
    print("必填欄位 (Required Fields):")
    print("-" * 40)
    for field in required_fields:
        print(f"  {field['name']} ({field['type']})")
        if field['help_text']:
            print(f"    說明: {field['help_text']}")
        if field['choices']:
            print(f"    選擇: {field['choices']}")
        print()
    
    # 顯示外鍵欄位
    print("外鍵欄位 (Foreign Key Fields):")
    print("-" * 40)
    for field in foreign_key_fields:
        required_str = "必填" if field['required'] else "選填"
        print(f"  {field['name']} ({field['type']}) - {required_str}")
        if field['help_text']:
            print(f"    說明: {field['help_text']}")
        if field['default'] is not None:
            print(f"    預設值: {field['default']}")
        print()
    
    # 顯示多對多欄位
    print("多對多欄位 (Many-to-Many Fields):")
    print("-" * 40)
    for field in many_to_many_fields:
        print(f"  {field['name']} ({field['type']}) - 選填")
        if field['help_text']:
            print(f"    說明: {field['help_text']}")
        print()
    
    # 顯示重要的選填欄位
    print("重要的選填欄位 (Important Optional Fields):")
    print("-" * 40)
    important_fields = ['is_public', 'date', 'license', 'summary', 'enable_ppa', 'enable_waveform']
    for field in optional_fields:
        if field['name'] in important_fields:
            print(f"  {field['name']} ({field['type']})")
            if field['help_text']:
                print(f"    說明: {field['help_text']}")
            if field['default'] is not None:
                print(f"    預設值: {field['default']}")
            print()
    
    # 顯示 Verilog 相關欄位
    print("Verilog 相關欄位 (Verilog-specific Fields):")
    print("-" * 40)
    verilog_fields = ['enable_waveform', 'enable_ppa', 'ppa_maximum_fmax', 'f4pga_board', 
                      'f4pga_target_fmax', 'openlane_pdk', 'openlane_ppa_score', 
                      'openlane_critical_path_ns', 'openlane_core_area_um2', 'openlane_power_total']
    for field in optional_fields:
        if field['name'] in verilog_fields:
            print(f"  {field['name']} ({field['type']})")
            if field['help_text']:
                print(f"    說明: {field['help_text']}")
            if field['default'] is not None:
                print(f"    預設值: {field['default']}")
            if field['choices']:
                print(f"    選擇: {field['choices']}")
            print()
    
    return {
        'required': required_fields,
        'foreign_key': foreign_key_fields,
        'many_to_many': many_to_many_fields,
        'optional': optional_fields
    }

if __name__ == '__main__':
    analyze_problem_fields()
