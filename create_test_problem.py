#!/usr/bin/env python3
"""
直接建立 Problem 到資料庫
"""
import os
import sys
import django

# 設定 Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')
sys.path.append('/home/xc/dmoj-site')
django.setup()

from judge.models import Problem, ProblemGroup, Language
from django.contrib.auth.models import User
from judge.models import Profile

def create_test_problem():
    """直接建立測試題目到資料庫"""
    
    # 檢查必要的依賴項目
    try:
        # 取得或建立 ProblemGroup
        group, created = ProblemGroup.objects.get_or_create(
            name='test',
            defaults={'full_name': '測試分類'}
        )
        if created:
            print(f"建立新的題目群組: {group}")
        
        # 取得 Verilog 語言
        try:
            verilog_lang = Language.objects.get(key='VLOG')
            print(f"找到 Verilog 語言: {verilog_lang}")
        except Language.DoesNotExist:
            print("錯誤: 找不到 Verilog 語言")
            return None
        
        # 建立測試題目
        problem_data = {
            'code': 'testverilog01',
            'name': '測試 Verilog 題目 - CPU 設計',
            'description': '''# CPU 設計挑戰

設計一個簡單的 RISC 處理器核心，需要支援基本的算術和邏輯運算指令。

## 需求
- 支持 ADD, SUB, AND, OR 指令
- 32-bit 資料路徑
- 單週期執行
- 包含暫存器檔案

## 輸入/輸出
- 輸入：指令記憶體和資料記憶體
- 輸出：計算結果和控制信號

## PPA 要求
- 最大關鍵路徑延遲: ≤ 10ns
- 核心面積: ≤ 50000μm²
- 總功耗: ≤ 100mW
- PPA 分數: ≥ 80
''',
            'time_limit': 30.0,
            'memory_limit': 262144,  # 256MB
            'points': 100.0,
            'group': group,
            'partial': True,
            'is_public': True,
            'is_manually_managed': False,
            
            # Verilog 相關設定
            'enable_waveform': True,
            'enable_ppa': True,
            'f4pga_board': 'arty_a7_100t',
            'f4pga_target_fmax': 100.0,
            'openlane_pdk': 'sky130A',
            'openlane_ppa_score': 80.0,
            'openlane_critical_path_ns': 10.0,
            'openlane_core_area_um2': 50000.0,
            'openlane_power_total': 100.0,
        }
        
        # 檢查題目是否已存在
        if Problem.objects.filter(code=problem_data['code']).exists():
            print(f"題目 {problem_data['code']} 已存在，將更新")
            problem = Problem.objects.get(code=problem_data['code'])
            for key, value in problem_data.items():
                setattr(problem, key, value)
            problem.save()
            action = "更新"
        else:
            problem = Problem.objects.create(**problem_data)
            action = "建立"
        
        # 設定允許的語言
        problem.allowed_languages.clear()
        problem.allowed_languages.add(verilog_lang)
        
        print(f"✅ 成功{action}題目:")
        print(f"  代碼: {problem.code}")
        print(f"  名稱: {problem.name}")
        print(f"  群組: {problem.group}")
        print(f"  時間限制: {problem.time_limit}秒")
        print(f"  記憶體限制: {problem.memory_limit}KB")
        print(f"  分數: {problem.points}")
        print(f"  公開: {problem.is_public}")
        print(f"  PPA 啟用: {problem.enable_ppa}")
        print(f"  波形啟用: {problem.enable_waveform}")
        print(f"  F4PGA 開發板: {problem.f4pga_board}")
        print(f"  OpenLane PDK: {problem.openlane_pdk}")
        print(f"  PPA 分數目標: {problem.openlane_ppa_score}")
        print(f"  關鍵路徑限制: {problem.openlane_critical_path_ns}ns")
        print(f"  面積限制: {problem.openlane_core_area_um2}μm²")
        print(f"  功耗限制: {problem.openlane_power_total}mW")
        print(f"  允許的語言: {[lang.name for lang in problem.allowed_languages.all()]}")
        
        return problem
        
    except Exception as e:
        print(f"錯誤: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_problem_access():
    """測試題目在管理介面中的顯示"""
    try:
        problem = Problem.objects.get(code='testverilog01')
        print(f"\n📋 題目詳細資訊 ({problem.code}):")
        print(f"  ID: {problem.id}")
        print(f"  名稱: {problem.name}")
        print(f"  enable_ppa: {problem.enable_ppa} (型別: {type(problem.enable_ppa)})")
        print(f"  enable_waveform: {problem.enable_waveform}")
        print(f"  f4pga_board: '{problem.f4pga_board}'")
        print(f"  openlane_pdk: '{problem.openlane_pdk}'")
        
        # 測試條件邏輯
        if problem.enable_ppa:
            print("  ✅ PPA 啟用 - 應該顯示 F4PGA/OpenLane 設定")
        else:
            print("  ❌ PPA 停用 - 應該顯示停用訊息")
            
        # 檢查語言設定
        languages = problem.allowed_languages.all()
        print(f"  允許的語言: {[lang.name for lang in languages]}")
        has_verilog = any('verilog' in lang.name.lower() or 'verilog' in lang.key.lower() for lang in languages)
        print(f"  包含 Verilog: {has_verilog}")
        
        return problem
        
    except Problem.DoesNotExist:
        print("❌ 找不到測試題目")
        return None

if __name__ == '__main__':
    print("=== 建立測試題目 ===")
    problem = create_test_problem()
    
    if problem:
        print("\n=== 測試題目存取 ===")
        test_problem_access()
        
        print(f"\n🌐 題目網址: http://127.0.0.1:8000/problem/{problem.code}")
        print(f"🛠️  管理網址: http://127.0.0.1:8000/admin/judge/problem/{problem.id}/change/")
