#!/usr/bin/env python
"""
測試增強版題目批量匯入腳本

此腳本用於測試 enhanced_bulk_import_problems.py 的功能
"""

import os
import sys
import subprocess
import tempfile
import csv
from datetime import datetime

# 設置 Django 環境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')

import django
django.setup()

from judge.models import Problem, ProblemGroup, ProblemType, Language, Profile


def create_test_csv():
    """創建測試用的 CSV 檔案"""
    # 創建臨時檔案
    fd, path = tempfile.mkstemp(suffix='.csv', text=True)
    
    try:
        with os.fdopen(fd, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'code', 'name', 'description', 'group', 'time_limit', 'memory_limit', 
                'points', 'types', 'authors', 'curators', 'testers', 'allowed_languages',
                'is_public', 'partial', 'short_circuit', 'is_manually_managed', 
                'license', 'og_image', 'summary', 'banned_users', 'organizations',
                'is_organization_private', 'enable_waveform', 'enable_ppa', 
                'ppa_maximum_fmax', 'f4pga_board', 'f4pga_target_fmax', 'openlane_pdk',
                'openlane_ppa_score', 'openlane_critical_path_ns', 'openlane_core_area_um2',
                'openlane_power_total', 'solution_content', 'solution_is_public', 
                'solution_authors', 'translation_en_name', 'translation_en_description',
                'translation_zh_hant_name', 'translation_zh_hant_description', 
                'clarifications', 'language_limits', 'is_full_markup'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # 測試資料 1：基本題目
            writer.writerow({
                'code': 'test001',
                'name': '測試加法器',
                'description': '這是一個測試用的加法器題目',
                'group': 'test',
                'time_limit': '2.0',
                'memory_limit': '262144',
                'points': '5.0',
                'types': 'Combinational Logic',
                'is_public': 'true',
                'enable_waveform': 'true',
                'enable_ppa': 'true',
                'ppa_maximum_fmax': '350.0',
                'f4pga_board': 'basys3',
                'f4pga_target_fmax': '300.0',
                'openlane_pdk': 'sky130A',
                'solution_content': 'module test_solution(); endmodule',
                'solution_is_public': 'true',
                'translation_en_name': 'Test Adder',
                'translation_en_description': 'This is a test adder problem',
                'clarifications': '請注意輸入時序;確保輸出穩定',
            })
            
            # 測試資料 2：複雜題目
            writer.writerow({
                'code': 'test002',
                'name': '測試計數器',
                'description': '這是一個測試用的計數器題目',
                'group': 'test',
                'time_limit': '3.0',
                'memory_limit': '524288',
                'points': '10.0',
                'types': 'Sequential Logic,Counters',
                'is_public': 'false',
                'partial': 'true',
                'enable_waveform': 'true',
                'enable_ppa': 'false',
                'solution_content': 'module counter(); endmodule',
                'solution_is_public': 'false',
                'translation_zh_hant_name': '測試計數器',
                'translation_zh_hant_description': '這是繁體中文描述',
            })
            
        return path
        
    except Exception:
        # 如果出錯，清理臨時檔案
        try:
            os.unlink(path)
        except:
            pass
        raise


def run_import_test(csv_path, dry_run=True):
    """運行匯入測試"""
    script_path = os.path.join(os.path.dirname(__file__), 'enhanced_bulk_import_problems.py')
    
    cmd = ['python', script_path, '--csv', csv_path]
    if dry_run:
        cmd.append('--dry-run')
    cmd.extend(['--log-level', 'DEBUG'])
    
    print(f"執行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)
        )
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"返回碼: {result.returncode}")
        return result.returncode == 0
        
    except Exception as e:
        print(f"執行錯誤: {e}")
        return False


def check_database():
    """檢查資料庫中的測試資料"""
    print("\n檢查資料庫中的測試題目:")
    
    test_problems = Problem.objects.filter(code__startswith='test')
    for problem in test_problems:
        print(f"- {problem.code}: {problem.name}")
        print(f"  群組: {problem.group}")
        print(f"  分數: {problem.points}")
        print(f"  公開: {problem.is_public}")
        print(f"  波形: {problem.enable_waveform}")
        print(f"  PPA: {problem.enable_ppa}")
        
        # 檢查翻譯
        translations = problem.translations.all()
        for trans in translations:
            print(f"  翻譯 ({trans.language}): {trans.name}")
        
        # 檢查解答
        if hasattr(problem, 'solution'):
            print(f"  解答: {'是' if problem.solution.is_public else '否'}")
        
        # 檢查澄清
        clarifications = problem.clarifications.all()
        print(f"  澄清數量: {clarifications.count()}")
        
        print()


def cleanup_test_data():
    """清理測試資料"""
    print("清理測試資料...")
    
    # 刪除測試題目
    deleted_count = Problem.objects.filter(code__startswith='test').delete()[0]
    print(f"刪除了 {deleted_count} 個測試題目")
    
    # 清理測試群組
    test_groups = ProblemGroup.objects.filter(name='test')
    if test_groups.exists():
        test_groups.delete()
        print("刪除了測試群組")


def main():
    """主測試函數"""
    print("=" * 60)
    print("DMOJ 增強版題目批量匯入測試")
    print("=" * 60)
    
    # 1. 創建測試 CSV
    print("1. 創建測試 CSV 檔案...")
    try:
        csv_path = create_test_csv()
        print(f"   測試 CSV 檔案: {csv_path}")
    except Exception as e:
        print(f"   創建 CSV 檔案失敗: {e}")
        return False
    
    try:
        # 2. 試運行測試
        print("\n2. 執行試運行測試...")
        if not run_import_test(csv_path, dry_run=True):
            print("   試運行測試失敗!")
            return False
        print("   試運行測試成功!")
        
        # 3. 實際匯入測試
        print("\n3. 執行實際匯入測試...")
        if not run_import_test(csv_path, dry_run=False):
            print("   實際匯入測試失敗!")
            return False
        print("   實際匯入測試成功!")
        
        # 4. 檢查資料庫
        print("\n4. 檢查資料庫...")
        check_database()
        
        # 5. 清理測試資料
        print("\n5. 清理測試資料...")
        cleanup_test_data()
        
        print("\n" + "=" * 60)
        print("所有測試完成!")
        print("=" * 60)
        return True
        
    finally:
        # 清理臨時 CSV 檔案
        try:
            os.unlink(csv_path)
            print(f"清理臨時檔案: {csv_path}")
        except:
            pass


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n測試被使用者中斷")
        sys.exit(1)
    except Exception as e:
        print(f"\n測試執行錯誤: {e}")
        sys.exit(1)