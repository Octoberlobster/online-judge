#!/usr/bin/env python
import csv
import io

# 讀取 CSV 檔案並檢查具體內容
csv_content = """code,name,description,group,time_limit,memory_limit,points,types,authors,curators,testers,allowed_languages,is_public,partial,short_circuit,is_manually_managed,license,og_image,summary,banned_users,organizations,is_organization_private,enable_waveform,enable_ppa,ppa_maximum_fmax,f4pga_board,f4pga_target_fmax,openlane_pdk,openlane_ppa_score,openlane_critical_path_ns,openlane_core_area_um2,openlane_power_total,solution_content,solution_is_public,solution_authors,translations_zh_hant,translations_en,clarifications,language_limits
counter_8bit,8位元計數器,設計一個8位元二進制計數器電路。計數器需要支援時脈輸入、重置功能，並能正確計數。,Demo,2.0,524288,150,Implementation,,,,,true,true,false,false,,,FPGA 計數器設計挑戰,,,false,true,true,100.0,basys3,80.0,,,,,,,設計一個8位元計數器模組。請實作時脈驅動的計數邏輯。,true,,8位元計數器:設計一個8位元二進制計數器電路。計數器需要支援時脈輸入、重置功能，並能正確計數。,8-bit Counter:Design an 8-bit binary counter circuit. The counter should support clock input and reset functionality.,計數器必須支援重置功能|頻率要達到指定要求,VLOG:3.0:1048576"""

csv_reader = csv.DictReader(io.StringIO(csv_content))

for row_num, row in enumerate(csv_reader, start=2):
    if row['code'] == 'counter_8bit':
        print(f"=== 檢查 {row['code']} 的翻譯欄位 ===")
        print(f"translations_zh_hant: '{row.get('translations_zh_hant', '')}'")
        print(f"translations_en: '{row.get('translations_en', '')}'")
        
        # 解析翻譯
        zh_hant_value = row.get('translations_zh_hant', '').strip()
        en_value = row.get('translations_en', '').strip()
        
        print(f"\n=== 解析結果 ===")
        
        if zh_hant_value:
            if ':' in zh_hant_value:
                zh_parts = zh_hant_value.split(':', 1)
                zh_name = zh_parts[0].strip()
                zh_desc = zh_parts[1].strip() if len(zh_parts) > 1 else ''
                print(f"繁體中文 - 名稱: '{zh_name}', 描述: '{zh_desc[:50]}...'")
            else:
                print(f"繁體中文 - 名稱: '{zh_hant_value}', 描述: ''")
        else:
            print("繁體中文: 無資料")
            
        if en_value:
            if ':' in en_value:
                en_parts = en_value.split(':', 1)
                en_name = en_parts[0].strip()
                en_desc = en_parts[1].strip() if len(en_parts) > 1 else ''
                print(f"英文 - 名稱: '{en_name}', 描述: '{en_desc[:50]}...'")
            else:
                print(f"英文 - 名稱: '{en_value}', 描述: ''")
        else:
            print("英文: 無資料")
        
        break