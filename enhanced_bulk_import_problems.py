#!/usr/bin/env python
"""
DMOJ 增強版題目批量匯入腳本

根據 enhanced_sample_problems.csv 格式設計的題目匯入工具，支援：
- 完整的題目資訊匯入（包含所有 CSV 欄位）
- Verilog 特色功能 (波形圖、PPA 分析、F4PGA、OpenLane)
- 多語言翻譯（英文和繁體中文）
- 解答內容匯入
- 關聯資料處理 (作者、組織、語言限制等)
- 題目澄清匯入

使用方法：
    python enhanced_bulk_import_problems.py --csv enhanced_sample_problems.csv [選項]

CSV 欄位對應：
- code: 題目代碼
- name: 題目名稱  
- description: 題目描述
- group: 題目群組
- time_limit: 時間限制
- memory_limit: 記憶體限制
- points: 分數
- types: 題目類型（多個用逗號分隔）
- authors: 作者（多個用逗號分隔）
- curators: 策展人（多個用逗號分隔）
- testers: 測試者（多個用逗號分隔）
- allowed_languages: 允許語言（多個用逗號分隔）
- is_public: 是否公開
- partial: 允許部分分數
- short_circuit: 短路評判
- is_manually_managed: 手動管理
- license: 授權許可
- og_image: OpenGraph 圖片
- summary: 題目摘要
- banned_users: 禁用使用者（多個用逗號分隔）
- organizations: 組織（多個用逗號分隔）
- is_organization_private: 組織私有
- enable_waveform: 啟用波形
- enable_ppa: 啟用 PPA
- ppa_maximum_fmax: 最大 PPA Fmax
- f4pga_board: F4PGA 開發板
- f4pga_target_fmax: F4PGA 目標頻率
- openlane_pdk: OpenLane PDK
- openlane_ppa_score: OpenLane PPA 分數
- openlane_critical_path_ns: OpenLane 關鍵路徑延遲
- openlane_core_area_um2: OpenLane 核心面積
- openlane_power_total: OpenLane 總功耗
- solution_content: 解答內容
- solution_is_public: 解答是否公開
- solution_authors: 解答作者（多個用逗號分隔）
- translation_en_name: 英文翻譯名稱
- translation_en_description: 英文翻譯描述
- translation_zh_hant_name: 繁體中文翻譯名稱
- translation_zh_hant_description: 繁體中文翻譯描述
- clarifications: 題目澄清（多個用分號分隔）
- language_limits: 語言限制（格式：language:time:memory;language:time:memory）
- is_full_markup: 完整標記語言
"""

import os
import sys
import csv
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

# 設置 Django 環境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')

try:
    import django
    django.setup()
except ImportError:
    print("錯誤: 無法匯入 Django。請確保在 DMOJ 環境中運行此腳本。")
    sys.exit(1)

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
from judge.models import (
    Problem, ProblemType, ProblemGroup, ProblemTranslation,
    ProblemClarification, Language, Profile, Organization, 
    License, Solution, LanguageLimit
)

# 設置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_bulk_import.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EnhancedBulkImporter:
    """增強版題目批量匯入器"""
    
    def __init__(self, dry_run: bool = False, skip_errors: bool = False):
        self.dry_run = dry_run
        self.skip_errors = skip_errors
        self.stats = {
            'total': 0,
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        # CSV 欄位映射
        self.csv_fields = [
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

    def parse_boolean(self, value: str) -> bool:
        """解析布林值"""
        if not value or value.strip() == '':
            return False
        return value.strip().lower() in ('true', '1', 'yes', 'on', 'enabled', '是', '啟用')

    def parse_float(self, value: str) -> Optional[float]:
        """解析浮點數"""
        if not value or value.strip() == '':
            return None
        try:
            return float(value.strip())
        except ValueError:
            return None

    def parse_int(self, value: str) -> Optional[int]:
        """解析整數"""
        if not value or value.strip() == '':
            return None
        try:
            return int(float(value.strip()))
        except ValueError:
            return None

    def parse_list(self, value: str, separator: str = ',') -> List[str]:
        """解析逗號分隔的列表"""
        if not value or value.strip() == '':
            return []
        return [item.strip() for item in value.split(separator) if item.strip()]

    def get_or_create_problem_group(self, group_name: str) -> ProblemGroup:
        """獲取或創建題目群組"""
        if not group_name:
            # 使用預設群組
            group_name = 'default'
            
        group, created = ProblemGroup.objects.get_or_create(
            name=group_name,
            defaults={'full_name': group_name.title()}
        )
        if created:
            logger.info(f"創建新題目群組: {group_name}")
        return group

    def get_or_create_problem_types(self, types_str: str) -> List[ProblemType]:
        """獲取或創建題目類型"""
        types_list = self.parse_list(types_str)
        problem_types = []
        
        for type_name in types_list:
            if not type_name:
                continue
                
            prob_type, created = ProblemType.objects.get_or_create(
                name=type_name,
                defaults={'full_name': type_name.title()}
            )
            if created:
                logger.info(f"創建新題目類型: {type_name}")
            problem_types.append(prob_type)
            
        return problem_types

    def get_profiles(self, usernames_str: str) -> List[Profile]:
        """獲取使用者檔案"""
        usernames = self.parse_list(usernames_str)
        profiles = []
        
        for username in usernames:
            try:
                profile = Profile.objects.get(user__username=username)
                profiles.append(profile)
            except Profile.DoesNotExist:
                logger.warning(f"找不到使用者: {username}")
                
        return profiles

    def get_languages(self, languages_str: str) -> List[Language]:
        """獲取程式語言"""
        language_names = self.parse_list(languages_str)
        languages = []
        
        for lang_name in language_names:
            try:
                # 先嘗試用 key 查找
                language = Language.objects.get(key=lang_name)
                languages.append(language)
            except Language.DoesNotExist:
                try:
                    # 再嘗試用 name 查找
                    language = Language.objects.get(name=lang_name)
                    languages.append(language)
                except Language.DoesNotExist:
                    logger.warning(f"找不到程式語言: {lang_name}")
                    
        return languages

    def get_organizations(self, org_names_str: str) -> List[Organization]:
        """獲取組織"""
        org_names = self.parse_list(org_names_str)
        organizations = []
        
        for org_name in org_names:
            try:
                org = Organization.objects.get(slug=org_name)
                organizations.append(org)
            except Organization.DoesNotExist:
                logger.warning(f"找不到組織: {org_name}")
                
        return organizations

    def get_license(self, license_key: str) -> Optional[License]:
        """獲取授權許可"""
        if not license_key:
            return None
            
        try:
            return License.objects.get(key=license_key)
        except License.DoesNotExist:
            logger.warning(f"找不到授權許可: {license_key}")
            return None

    def parse_language_limits(self, limits_str: str) -> List[Dict[str, Any]]:
        """解析語言限制設定"""
        if not limits_str:
            return []
            
        limits = []
        # 格式：language:time:memory;language:time:memory
        for limit_spec in limits_str.split(';'):
            limit_spec = limit_spec.strip()
            if not limit_spec:
                continue
                
            parts = limit_spec.split(':')
            if len(parts) != 3:
                logger.warning(f"語言限制格式錯誤: {limit_spec}")
                continue
                
            language_key, time_limit, memory_limit = [p.strip() for p in parts]
            
            try:
                language = Language.objects.get(key=language_key)
                limits.append({
                    'language': language,
                    'time_limit': float(time_limit),
                    'memory_limit': int(float(memory_limit))
                })
            except (Language.DoesNotExist, ValueError) as e:
                logger.warning(f"語言限制解析錯誤 {limit_spec}: {e}")
                
        return limits

    def create_or_update_problem(self, row: Dict[str, str]) -> Optional[Problem]:
        """創建或更新題目"""
        code = row.get('code', '').strip()
        if not code:
            logger.error("題目代碼為空，跳過此行")
            return None

        try:
            with transaction.atomic():
                # 檢查題目是否存在
                problem, created = Problem.objects.get_or_create(
                    code=code,
                    defaults={}
                )
                
                # 設置基本欄位
                problem.name = row.get('name', '').strip() or code
                problem.description = row.get('description', '').strip()
                
                # 設置群組
                group_name = row.get('group', '').strip()
                if group_name:
                    problem.group = self.get_or_create_problem_group(group_name)
                
                # 設置數值欄位
                problem.time_limit = self.parse_float(row.get('time_limit')) or 1.0
                problem.memory_limit = self.parse_int(row.get('memory_limit')) or 262144
                problem.points = self.parse_float(row.get('points')) or 1.0
                
                # 設置布林欄位
                problem.is_public = self.parse_boolean(row.get('is_public'))
                problem.partial = self.parse_boolean(row.get('partial'))
                problem.short_circuit = self.parse_boolean(row.get('short_circuit'))
                problem.is_manually_managed = self.parse_boolean(row.get('is_manually_managed'))
                problem.is_organization_private = self.parse_boolean(row.get('is_organization_private'))
                problem.is_full_markup = self.parse_boolean(row.get('is_full_markup'))
                
                # 設置其他欄位
                problem.og_image = row.get('og_image', '').strip()
                problem.summary = row.get('summary', '').strip()
                
                # 設置授權許可
                license_key = row.get('license', '').strip()
                if license_key:
                    problem.license = self.get_license(license_key)
                
                # Verilog 相關欄位
                problem.enable_waveform = self.parse_boolean(row.get('enable_waveform'))
                problem.enable_ppa = self.parse_boolean(row.get('enable_ppa'))
                problem.ppa_maximum_fmax = self.parse_float(row.get('ppa_maximum_fmax'))
                problem.f4pga_board = row.get('f4pga_board', '').strip()
                problem.f4pga_target_fmax = self.parse_float(row.get('f4pga_target_fmax'))
                problem.openlane_pdk = row.get('openlane_pdk', '').strip()
                problem.openlane_ppa_score = self.parse_float(row.get('openlane_ppa_score'))
                problem.openlane_critical_path_ns = self.parse_float(row.get('openlane_critical_path_ns'))
                problem.openlane_core_area_um2 = self.parse_float(row.get('openlane_core_area_um2'))
                problem.openlane_power_total = self.parse_float(row.get('openlane_power_total'))
                
                # 設置發布日期
                if problem.is_public and not problem.date:
                    problem.date = timezone.now()
                
                if not self.dry_run:
                    problem.save()
                
                # 處理多對多關係
                if not self.dry_run:
                    self.handle_many_to_many_relations(problem, row)
                    self.handle_translations(problem, row)
                    self.handle_solution(problem, row)
                    self.handle_clarifications(problem, row)
                    self.handle_language_limits(problem, row)
                
                if created:
                    self.stats['created'] += 1
                    logger.info(f"創建題目: {code}")
                else:
                    self.stats['updated'] += 1
                    logger.info(f"更新題目: {code}")
                
                return problem
                
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"處理題目 {code} 時發生錯誤: {e}")
            if not self.skip_errors:
                raise
            return None

    def handle_many_to_many_relations(self, problem: Problem, row: Dict[str, str]):
        """處理多對多關係"""
        # 處理題目類型
        types_str = row.get('types', '').strip()
        if types_str:
            problem_types = self.get_or_create_problem_types(types_str)
            problem.types.set(problem_types)
        
        # 處理作者
        authors_str = row.get('authors', '').strip()
        if authors_str:
            authors = self.get_profiles(authors_str)
            problem.authors.set(authors)
        
        # 處理策展人
        curators_str = row.get('curators', '').strip()
        if curators_str:
            curators = self.get_profiles(curators_str)
            problem.curators.set(curators)
        
        # 處理測試者
        testers_str = row.get('testers', '').strip()
        if testers_str:
            testers = self.get_profiles(testers_str)
            problem.testers.set(testers)
        
        # 處理允許語言
        languages_str = row.get('allowed_languages', '').strip()
        if languages_str:
            languages = self.get_languages(languages_str)
            problem.allowed_languages.set(languages)
        
        # 處理禁用使用者
        banned_users_str = row.get('banned_users', '').strip()
        if banned_users_str:
            banned_users = self.get_profiles(banned_users_str)
            problem.banned_users.set(banned_users)
        
        # 處理組織
        organizations_str = row.get('organizations', '').strip()
        if organizations_str:
            organizations = self.get_organizations(organizations_str)
            problem.organizations.set(organizations)

    def handle_translations(self, problem: Problem, row: Dict[str, str]):
        """處理翻譯"""
        logger.debug(f"處理 {problem.code} 的翻譯")
        
        # 英文翻譯
        en_name = row.get('translation_en_name', '').strip()
        en_description = row.get('translation_en_description', '').strip()
        if en_name or en_description:
            logger.debug(f"處理英文翻譯: {en_name} / {en_description[:50]}...")
            translation, created = ProblemTranslation.objects.get_or_create(
                problem=problem,
                language='en',
                defaults={
                    'name': en_name or problem.name,
                    'description': en_description or problem.description
                }
            )
            if not created:
                logger.debug("更新現有英文翻譯")
                if en_name:
                    translation.name = en_name
                if en_description:
                    translation.description = en_description
                translation.save()
            else:
                logger.debug("創建新的英文翻譯")
        
        # 繁體中文翻譯
        zh_name = row.get('translation_zh_hant_name', '').strip()
        zh_description = row.get('translation_zh_hant_description', '').strip()
        if zh_name or zh_description:
            logger.debug(f"處理繁體中文翻譯: {zh_name} / {zh_description[:50]}...")
            translation, created = ProblemTranslation.objects.get_or_create(
                problem=problem,
                language='zh-hant',
                defaults={
                    'name': zh_name or problem.name,
                    'description': zh_description or problem.description
                }
            )
            if not created:
                logger.debug("更新現有繁體中文翻譯")
                if zh_name:
                    translation.name = zh_name
                if zh_description:
                    translation.description = zh_description
                translation.save()
            else:
                logger.debug("創建新的繁體中文翻譯")

    def handle_solution(self, problem: Problem, row: Dict[str, str]):
        """處理解答"""
        solution_content = row.get('solution_content', '').strip()
        if not solution_content:
            return
        
        solution_is_public = self.parse_boolean(row.get('solution_is_public'))
        solution_authors_str = row.get('solution_authors', '').strip()
        
        solution, created = Solution.objects.get_or_create(
            problem=problem,
            defaults={
                'content': solution_content,
                'is_public': solution_is_public,
                'publish_on': timezone.now()
            }
        )
        
        if not created:
            solution.content = solution_content
            solution.is_public = solution_is_public
            solution.save()
        
        # 設置解答作者
        if solution_authors_str:
            solution_authors = self.get_profiles(solution_authors_str)
            solution.authors.set(solution_authors)

    def handle_clarifications(self, problem: Problem, row: Dict[str, str]):
        """處理題目澄清"""
        clarifications_str = row.get('clarifications', '').strip()
        if not clarifications_str:
            return
        
        # 清除現有澄清
        ProblemClarification.objects.filter(problem=problem).delete()
        
        # 添加新澄清（用分號分隔）
        clarifications = self.parse_list(clarifications_str, ';')
        for clarification_text in clarifications:
            if clarification_text:
                ProblemClarification.objects.create(
                    problem=problem,
                    description=clarification_text
                )

    def handle_language_limits(self, problem: Problem, row: Dict[str, str]):
        """處理語言限制"""
        limits_str = row.get('language_limits', '').strip()
        if not limits_str:
            return
        
        # 清除現有語言限制
        LanguageLimit.objects.filter(problem=problem).delete()
        
        # 添加新語言限制
        limits = self.parse_language_limits(limits_str)
        for limit in limits:
            LanguageLimit.objects.create(
                problem=problem,
                language=limit['language'],
                time_limit=limit['time_limit'],
                memory_limit=limit['memory_limit']
            )

    def import_from_csv(self, csv_file_path: str):
        """從 CSV 檔案匯入題目"""
        logger.info(f"開始匯入 CSV 檔案: {csv_file_path}")
        
        if not os.path.exists(csv_file_path):
            raise FileNotFoundError(f"找不到檔案: {csv_file_path}")
        
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
                # 自動檢測 CSV 方言
                dialect = csv.Sniffer().sniff(csvfile.read(1024))
                csvfile.seek(0)
                
                reader = csv.DictReader(csvfile, dialect=dialect)
                
                # 驗證 CSV 標題
                missing_fields = set(self.csv_fields) - set(reader.fieldnames)
                if missing_fields:
                    logger.warning(f"CSV 檔案缺少欄位: {missing_fields}")
                
                for row_num, row in enumerate(reader, start=2):
                    self.stats['total'] += 1
                    
                    # 跳過空行
                    if not any(row.values()):
                        self.stats['skipped'] += 1
                        continue
                    
                    logger.info(f"處理第 {row_num} 行: {row.get('code', '未知')}")
                    
                    try:
                        problem = self.create_or_update_problem(row)
                        if problem is None:
                            self.stats['skipped'] += 1
                    except Exception as e:
                        self.stats['errors'] += 1
                        logger.error(f"第 {row_num} 行處理失敗: {e}")
                        if not self.skip_errors:
                            raise
                
        except Exception as e:
            logger.error(f"讀取 CSV 檔案時發生錯誤: {e}")
            raise
        
        self.print_summary()

    def print_summary(self):
        """列印匯入摘要"""
        logger.info("=" * 50)
        logger.info("匯入摘要:")
        logger.info(f"總計處理: {self.stats['total']} 行")
        logger.info(f"創建題目: {self.stats['created']} 個")
        logger.info(f"更新題目: {self.stats['updated']} 個")
        logger.info(f"跳過: {self.stats['skipped']} 行")
        logger.info(f"錯誤: {self.stats['errors']} 行")
        
        if self.dry_run:
            logger.info("*** 這是試運行，沒有實際修改資料庫 ***")
        
        logger.info("=" * 50)


def main():
    """主函數"""
    parser = argparse.ArgumentParser(
        description='DMOJ 增強版題目批量匯入工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例用法:
  python enhanced_bulk_import_problems.py --csv enhanced_sample_problems.csv
  python enhanced_bulk_import_problems.py --csv data.csv --dry-run
  python enhanced_bulk_import_problems.py --csv data.csv --skip-errors
        """
    )
    
    parser.add_argument(
        '--csv', 
        required=True,
        help='CSV 檔案路徑'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='試運行模式，不實際修改資料庫'
    )
    
    parser.add_argument(
        '--skip-errors',
        action='store_true',
        help='跳過錯誤繼續處理'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='日誌等級'
    )
    
    args = parser.parse_args()
    
    # 設置日誌等級
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    try:
        importer = EnhancedBulkImporter(
            dry_run=args.dry_run,
            skip_errors=args.skip_errors
        )
        importer.import_from_csv(args.csv)
        
    except KeyboardInterrupt:
        logger.info("使用者中斷操作")
        sys.exit(1)
    except Exception as e:
        logger.error(f"匯入失敗: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()