import csv
import io
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from judge.models import Problem, ProblemGroup, ProblemType, Language, Profile


class CSVImportForm(forms.Form):
    csv_file = forms.FileField(
        label=_('CSV 文件'),
        help_text=_('上傳包含題目資料的 CSV 文件。文件應包含以下欄位：code, name, description, group, types, time_limit, memory_limit, points, authors, allowed_languages'),
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
        code = row.get('code', '').strip()
        if not code:
            errors.append(_('題目代碼不能為空'))
        elif Problem.objects.filter(code=code).exists():
            errors.append(_('題目代碼 "%(code)s" 已存在') % {'code': code})
        elif not code.isalnum() or not code.islower():
            errors.append(_('題目代碼必須是小寫字母和數字組成'))
        
        # 驗證題目名稱
        name = row.get('name', '').strip()
        if not name:
            errors.append(_('題目名稱不能為空'))
        
        # 驗證題目描述
        description = row.get('description', '').strip()
        if not description:
            errors.append(_('題目描述不能為空'))
        
        # 驗證題目組別
        group_name = row.get('group', '').strip()
        try:
            group = ProblemGroup.objects.get(name=group_name)
        except ProblemGroup.DoesNotExist:
            errors.append(_('題目組別 "%(group)s" 不存在') % {'group': group_name})
            group = None
        
        # 驗證時間限制
        try:
            time_limit = float(row.get('time_limit', 0))
            if time_limit <= 0:
                errors.append(_('時間限制必須大於 0'))
        except (ValueError, TypeError):
            errors.append(_('時間限制必須是有效的數字'))
            time_limit = None
        
        # 驗證記憶體限制
        try:
            memory_limit = int(row.get('memory_limit', 0))
            if memory_limit <= 0:
                errors.append(_('記憶體限制必須大於 0'))
        except (ValueError, TypeError):
            errors.append(_('記憶體限制必須是有效的整數'))
            memory_limit = None
        
        # 驗證分數
        try:
            points = float(row.get('points', 0))
            if points < 0:
                errors.append(_('分數不能為負數'))
        except (ValueError, TypeError):
            errors.append(_('分數必須是有效的數字'))
            points = None
        
        # 驗證題目類型（可選）
        types_str = row.get('types', '').strip()
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
        authors_str = row.get('authors', '').strip()
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
        languages_str = row.get('allowed_languages', '').strip()
        allowed_languages = []
        if languages_str:
            language_names = [l.strip() for l in languages_str.split(',')]
            for language_name in language_names:
                try:
                    language = Language.objects.get(name=language_name)
                    allowed_languages.append(language)
                except Language.DoesNotExist:
                    errors.append(_('程式語言 "%(language)s" 不存在') % {'language': language_name})
        
        if errors:
            raise ValidationError(errors)
        
        return {
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
            'is_public': row.get('is_public', '').strip().lower() in ('true', '1', 'yes'),
            'partial': row.get('partial', '').strip().lower() in ('true', '1', 'yes'),
            'short_circuit': row.get('short_circuit', '').strip().lower() in ('true', '1', 'yes'),
        }
