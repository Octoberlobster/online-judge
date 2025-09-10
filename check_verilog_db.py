#!/usr/bin/env python3
import os
import sys
import django

# 設定 Django 環境
sys.path.append('/home/xc/dmoj-site')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')
django.setup()

from judge.models import Problem

def check_verilog_problems_in_db():
    """檢查資料庫中現有的 Verilog 問題"""
    
    # 找出所有 Verilog 相關的題目
    problems = Problem.objects.filter(allowed_languages__name='Verilog')
    
    print(f"資料庫中共有 {problems.count()} 個 Verilog 題目")
    print("=" * 80)
    
    for problem in problems:
        print(f"\n📝 題目: {problem.code} - {problem.name}")
        print(f"   語言: {[lang.name for lang in problem.allowed_languages.all()]}")
        
        # 檢查 Verilog 設定
        print("\n📟 Verilog 設定:")
        print(f"   啟用波形: {problem.enable_waveform}")
        print(f"   啟用 PPA: {problem.enable_ppa}")
        print(f"   F4PGA 開發板: {problem.f4pga_board}")
        print(f"   F4PGA 目標頻率: {problem.f4pga_target_fmax}")
        print(f"   OpenLane PDK: {problem.openlane_pdk}")
        print(f"   PPA 分數: {problem.openlane_ppa_score}")
        print(f"   關鍵路徑 (ns): {problem.openlane_critical_path_ns}")
        print(f"   核心面積 (μm²): {problem.openlane_core_area_um2}")
        print(f"   總功耗 (mW): {problem.openlane_power_total}")
        print("-" * 60)

if __name__ == '__main__':
    check_verilog_problems_in_db()
