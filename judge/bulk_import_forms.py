import csv
import io
from datetime import datetime
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from judge.models import Problem, ProblemGroup, ProblemType, Language, Profile, Solution, ProblemTranslation


class CSVImportForm(forms.Form):
    csv_file = forms.FileField(
        label=_('CSV 文件'),
        help_text=_('上傳包含題目資料的 CSV 文件。文件應包含以下欄位：code, name, description, group, types, time_limit, memory_limit, points, authors, allowed_languages。可選欄位：solution_content, solution_is_public, solution_publish_on, translations (格式: lang:name:description,lang:name:description...)'),
        widget=forms.ClearableFileInput(attrs={'accept': '.csv'})
    )
    
    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']
        
        if not csv_file.name.endswith('.csv'):
            raise ValidationError(_('文件必須是 CSV 格式'))
        
        # 檢查文件大小（限制為 5MB）
        if csv_file.size > 5 * 1024 * 1024:
            raise ValidationError(_('文件大小不能超過 5MB'))
            
        return csv_file
    
    def process_csv(self):
        """處理 CSV 文件並返回待創建的題目列表"""
        csv_file = self.cleaned_data['csv_file']
        
        # 讀取 CSV 內容
        csv_content = csv_file.read().decode('utf-8-sig')  # 支援 BOM
        csv_file.seek(0)  # 重置文件指針
        
        reader = csv.DictReader(io.StringIO(csv_content))
        
        # 驗證必要的欄位
        required_fields = ['code', 'name', 'description', 'group', 'time_limit', 'memory_limit', 'points']
        missing_fields = [field for field in required_fields if field not in reader.fieldnames]
        if missing_fields:
            raise ValidationError(
                _('CSV 文件缺少必要欄位: %(fields)s') % {'fields': ', '.join(missing_fields)}
            )
        
        problems_to_create = []
        errors = []
        
        for row_num, row in enumerate(reader, start=2):  # 從第2行開始計算（第1行是標題）
            try:
                problem_data = self._validate_row(row, row_num)
                problems_to_create.append(problem_data)
            except ValidationError as e:
                errors.append(f'第 {row_num} 行: {", ".join(e.messages)}')
        
        if errors:
            raise ValidationError(_('CSV 文件有以下錯誤:\n%(errors)s') % {'errors': '\n'.join(errors)})
        
        return problems_to_create
    
    def _validate_row(self, row, row_num):
        """驗證單行資料"""
        errors = []
        
        # 驗證題目代碼
        code = (row.get('code', '') or '').strip()
        # 移除可能的 BOM 字符
        code = code.lstrip('\ufeff')
        if not code:
            errors.append(_('題目代碼不能為空'))
        elif Problem.objects.filter(code=code).exists():
            errors.append(_('題目代碼 "%(code)s" 已存在') % {'code': code})
        elif not code.replace('_', '').isalnum() or not code.islower():
            errors.append(_('題目代碼必須是小寫字母、數字和下劃線組成'))
        
        # 驗證題目名稱
        name = (row.get('name', '') or '').strip()
        if not name:
            errors.append(_('題目名稱不能為空'))
        
        # 驗證題目描述
        description = (row.get('description', '') or '').strip()
        if not description:
            errors.append(_('題目描述不能為空'))
        
        # 驗證題目組別
        group_name = (row.get('group', '') or '').strip()
        try:
            group = ProblemGroup.objects.get(name=group_name)
        except ProblemGroup.DoesNotExist:
            errors.append(_('題目組別 "%(group)s" 不存在') % {'group': group_name})
            group = None
        
        # 驗證時間限制
        try:
            time_limit = float(row.get('time_limit', 0) or 0)
            if time_limit <= 0:
                errors.append(_('時間限制必須大於 0'))
        except (ValueError, TypeError):
            errors.append(_('時間限制必須是有效的數字'))
            time_limit = None
        
        # 驗證記憶體限制
        try:
            memory_limit = int(row.get('memory_limit', 0) or 0)
            if memory_limit <= 0:
                errors.append(_('記憶體限制必須大於 0'))
        except (ValueError, TypeError):
            errors.append(_('記憶體限制必須是有效的整數'))
            memory_limit = None
        
        # 驗證分數
        try:
            points = float(row.get('points', 0) or 0)
            if points < 0:
                errors.append(_('分數不能為負數'))
        except (ValueError, TypeError):
            errors.append(_('分數必須是有效的數字'))
            points = None
        
        # 驗證題目類型（可選）
        types_str = (row.get('types', '') or '').strip()
        types = []
        if types_str:
            type_names = [t.strip() for t in types_str.split(',')]
            for type_name in type_names:
                try:
                    problem_type = ProblemType.objects.get(name=type_name)
                    types.append(problem_type)
                except ProblemType.DoesNotExist:
                    errors.append(_('題目類型 "%(type)s" 不存在') % {'type': type_name})
        
        # 驗證作者（可選）
        authors_str = (row.get('authors', '') or '').strip()
        authors = []
        if authors_str:
            author_usernames = [a.strip() for a in authors_str.split(',')]
            for username in author_usernames:
                try:
                    author = Profile.objects.get(user__username=username)
                    authors.append(author)
                except Profile.DoesNotExist:
                    errors.append(_('作者 "%(author)s" 不存在') % {'author': username})
        
        # 驗證允許的程式語言（可選）
        languages_str = (row.get('allowed_languages', '') or '').strip()
        allowed_languages = []
        if languages_str:
            language_names = [l.strip() for l in languages_str.split(',')]
            for language_name in language_names:
                language = self._find_language(language_name)
                if language:
                    allowed_languages.append(language)
                else:
                    errors.append(_('程式語言 "%(language)s" 不存在') % {'language': language_name})
        
        # 驗證題解（可選）
        solution_data = self._validate_solution(row, errors)
        
        # 驗證翻譯（可選）
        translations_data = self._validate_translations(row, errors)
        
        if errors:
            raise ValidationError(errors)
        
        problem_data = {
            'code': code,
            'name': name,
            'description': description,
            'group': group,
            'types': types,
            'time_limit': time_limit,
            'memory_limit': memory_limit,
            'points': points,
            'authors': authors,
            'allowed_languages': allowed_languages,
            'is_public': (row.get('is_public', '') or '').strip().lower() in ('true', '1', 'yes'),
            'partial': (row.get('partial', '') or '').strip().lower() in ('true', '1', 'yes'),
            'short_circuit': (row.get('short_circuit', '') or '').strip().lower() in ('true', '1', 'yes'),
        }
        
        if solution_data:
            problem_data['solution'] = solution_data
            
        if translations_data:
            problem_data['translations'] = translations_data
            
        return problem_data
    
    def _find_language(self, language_name):
        """
        根據語言名稱查找語言物件，支援多種識別方式：
        - name (如 "Verilog")
        - common_name (如 "verilog12") 
        - short_name (如 "verilog")
        """
        # 先嘗試用 name 查找
        try:
            return Language.objects.get(name=language_name)
        except Language.DoesNotExist:
            pass
        
        # 再嘗試用 common_name 查找
        try:
            return Language.objects.get(common_name=language_name)
        except Language.DoesNotExist:
            pass
        
        # 最後嘗試用 short_name 查找
        try:
            return Language.objects.get(short_name=language_name)
        except Language.DoesNotExist:
            pass
        
        return None
    
    def _validate_solution(self, row, errors):
        """驗證題解資料"""
        solution_content = row.get('solution_content', '') or ''
        solution_content = solution_content.strip()
        if not solution_content:
            return None
        
        solution_data = {
            'content': solution_content,
            'is_public': (row.get('solution_is_public', '') or '').strip().lower() in ('true', '1', 'yes'),
        }
        
        # 處理發布日期
        publish_on_str = (row.get('solution_publish_on', '') or '').strip()
        if publish_on_str:
            try:
                # 支援多種日期格式
                for date_format in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d', '%Y/%m/%d %H:%M:%S']:
                    try:
                        publish_on = datetime.strptime(publish_on_str, date_format)
                        solution_data['publish_on'] = timezone.make_aware(publish_on)
                        break
                    except ValueError:
                        continue
                else:
                    errors.append(_('題解發布日期格式不正確: "%(date)s"。請使用 YYYY-MM-DD 或 YYYY-MM-DD HH:MM:SS 格式') % {'date': publish_on_str})
                    return None
            except Exception:
                errors.append(_('題解發布日期格式不正確: "%(date)s"') % {'date': publish_on_str})
                return None
        else:
            # 如果沒有指定發布日期，預設為現在
            solution_data['publish_on'] = timezone.now()
        
        # 處理題解作者（可選）
        solution_authors_str = (row.get('solution_authors', '') or '').strip()
        solution_authors = []
        if solution_authors_str:
            author_usernames = [a.strip() for a in solution_authors_str.split(',')]
            for username in author_usernames:
                try:
                    author = Profile.objects.get(user__username=username)
                    solution_authors.append(author)
                except Profile.DoesNotExist:
                    errors.append(_('題解作者 "%(author)s" 不存在') % {'author': username})
        
        solution_data['authors'] = solution_authors
        return solution_data
    
    def _validate_translations(self, row, errors):
        """驗證翻譯資料"""
        translations_str = row.get('translations', '') or ''
        translations_str = translations_str.strip()
        if not translations_str:
            return None
        
        translations_data = []
        
        # 格式: lang1:name1:description1,lang2:name2:description2
        translation_entries = [t.strip() for t in translations_str.split(',')]
        
        valid_language_codes = [code for code, _ in settings.LANGUAGES]
        
        for entry in translation_entries:
            if not entry:
                continue
                
            parts = entry.split(':', 2)  # 最多分割成3部分
            if len(parts) != 3:
                errors.append(_('翻譯格式不正確: "%(entry)s"。正確格式為: 語言代碼:翻譯名稱:翻譯描述') % {'entry': entry})
                continue
            
            lang_code, trans_name, trans_description = [p.strip() for p in parts]
            
            # 驗證語言代碼
            if lang_code not in valid_language_codes:
                errors.append(_('不支援的語言代碼: "%(code)s"。支援的語言代碼: %(codes)s') % {
                    'code': lang_code,
                    'codes': ', '.join(valid_language_codes)
                })
                continue
            
            # 驗證翻譯名稱和描述
            if not trans_name:
                errors.append(_('語言 "%(lang)s" 的翻譯名稱不能為空') % {'lang': lang_code})
                continue
                
            if not trans_description:
                errors.append(_('語言 "%(lang)s" 的翻譯描述不能為空') % {'lang': lang_code})
                continue
            
            translations_data.append({
                'language': lang_code,
                'name': trans_name,
                'description': trans_description,
            })
        
        return translations_data if translations_data else None
