import csv
import io
from django import forms
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.forms import FileField
from django.core.exceptions import ValidationError


class CSVImportForm(forms.Form):
    csv_file = FileField(
        label='CSV File',
        help_text='Upload a CSV file containing problem data. The file should include fields: '
                  'code, name, description, group, time_limit, memory_limit, points, allowed_languages. '
                  'For Verilog problems, additional fields are available: enable_waveform, enable_ppa, '
                  'f4pga_board, f4pga_target_fmax, openlane_pdk, openlane_ppa_score, etc. '
                  'When enable_ppa=false, all PPA-related fields are ignored regardless of their values.',
        required=True
    )
    
    def clean_csv_file(self):
        csv_file = self.cleaned_data['csv_file']
        if csv_file:
            if not csv_file.name.endswith('.csv'):
                raise forms.ValidationError('File must be a CSV file')
            
            # Check file size (limit to 10MB)
            if csv_file.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size must be less than 10MB')
        
        return csv_file
    
    def process_csv(self):
        """Process the uploaded CSV file and return problem data"""
        csv_file = self.cleaned_data['csv_file']
        
        # Read the file content
        if hasattr(csv_file, 'read'):
            content = csv_file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8-sig')
        else:
            raise ValidationError('Invalid file format')
        
        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(content))
        problems_data = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # start=2 because header is row 1
            try:
                problem_data = self._process_row(row, row_num)
                if problem_data:
                    problems_data.append(problem_data)
            except Exception as e:
                raise ValidationError(f'Error processing row {row_num}: {str(e)}')
        
        return problems_data
    
    def _process_row(self, row, row_num):
        """Process a single CSV row and return problem data"""
        # Basic validation
        if not row.get('code') or not row.get('name'):
            return None  # Skip empty rows
        
        # Extract basic fields
        problem_data = {
            'code': row.get('code', '').strip(),
            'name': row.get('name', '').strip(),
            'description': row.get('description', ''),
            'time_limit': float(row.get('time_limit', 1.0)),
            'memory_limit': int(row.get('memory_limit', 262144)),
            'points': float(row.get('points', 100)),
            'is_public': self._parse_boolean(row.get('is_public', 'false')),
            'partial': self._parse_boolean(row.get('partial', 'false')),
            'short_circuit': self._parse_boolean(row.get('short_circuit', 'false')),
            'is_manually_managed': self._parse_boolean(row.get('is_manually_managed', 'false')),
        }
        
        # Process Verilog-specific fields
        enable_waveform = self._parse_boolean(row.get('enable_waveform', 'false'))
        enable_ppa = self._parse_boolean(row.get('enable_ppa', 'false'))
        
        problem_data['enable_waveform'] = enable_waveform
        problem_data['enable_ppa'] = enable_ppa
        
        # PPA 相關欄位的智能處理
        self._process_ppa_fields(row, problem_data, enable_ppa)
        
        # Process other fields
        self._process_additional_fields(row, problem_data)
        
        return problem_data
    
    def _parse_boolean(self, value):
        """Parse boolean values from CSV"""
        if isinstance(value, str):
            return value.lower().strip() in ('true', '1', 'yes', 'on')
        return bool(value)
    
    def _parse_float_or_none(self, value):
        """Parse float value or return None if invalid"""
        if not value or (isinstance(value, str) and not value.strip()):
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _process_ppa_fields(self, row, problem_data, enable_ppa):
        """Process PPA-related fields based on enable_ppa setting and CSV data"""
        
        # 初始化所有 PPA 欄位為預設值
        problem_data['ppa_maximum_fmax'] = None
        problem_data['f4pga_board'] = ''
        problem_data['f4pga_target_fmax'] = None
        problem_data['openlane_pdk'] = ''
        problem_data['openlane_ppa_score'] = None
        problem_data['openlane_critical_path_ns'] = None
        problem_data['openlane_core_area_um2'] = None
        problem_data['openlane_power_total'] = None
        
        # 只有當 enable_ppa 為 True 時才處理 PPA 欄位
        if not enable_ppa:
            return
        
        # 智能判斷：根據 CSV 檔案中的資料來判斷該啟用哪些功能
        # F4PGA 需要同時有開發板和目標頻率才算完整設定
        f4pga_board = row.get('f4pga_board', '').strip()
        f4pga_target_fmax = self._parse_float_or_none(row.get('f4pga_target_fmax'))
        has_f4pga_data = bool(f4pga_board and f4pga_target_fmax is not None)
        
        has_openlane_data = (
            row.get('openlane_pdk', '').strip() or
            row.get('openlane_ppa_score', '').strip() or
            row.get('openlane_critical_path_ns', '').strip() or
            row.get('openlane_core_area_um2', '').strip() or
            row.get('openlane_power_total', '').strip()
        )
        
        # PPA 最大頻率限制（通用設定）
        problem_data['ppa_maximum_fmax'] = self._parse_float_or_none(row.get('ppa_maximum_fmax'))
        
        # F4PGA 設定：只有當有完整的 F4PGA 資料時才處理
        if has_f4pga_data:
            problem_data['f4pga_board'] = f4pga_board
            problem_data['f4pga_target_fmax'] = f4pga_target_fmax
            
            # 驗證 F4PGA 開發板選項
            valid_boards = ['basys3', 'arty_a7_35t', 'arty_a7_100t', 'nexys4_ddr', 'nexys_video', 'zybo_z7']
            if problem_data['f4pga_board'] and problem_data['f4pga_board'] not in valid_boards:
                raise ValidationError(f'Row {row_num}: Invalid F4PGA board "{problem_data["f4pga_board"]}". Valid options: {", ".join(valid_boards)}')
        elif f4pga_board or f4pga_target_fmax is not None:
            # 如果只有部分 F4PGA 資料，發出警告但不阻止匯入
            print(f"Warning: Row has incomplete F4PGA data (board: '{f4pga_board}', target_fmax: {f4pga_target_fmax})")
        
        # OpenLane 設定：只有當有 OpenLane 相關資料時才處理
        if has_openlane_data:
            problem_data['openlane_pdk'] = row.get('openlane_pdk', '').strip()
            problem_data['openlane_ppa_score'] = self._parse_float_or_none(row.get('openlane_ppa_score'))
            problem_data['openlane_critical_path_ns'] = self._parse_float_or_none(row.get('openlane_critical_path_ns'))
            problem_data['openlane_core_area_um2'] = self._parse_float_or_none(row.get('openlane_core_area_um2'))
            problem_data['openlane_power_total'] = self._parse_float_or_none(row.get('openlane_power_total'))
            
            # 驗證 OpenLane PDK 選項
            valid_pdks = ['sky130A', 'sky130B', 'gf180mcuC']
            if problem_data['openlane_pdk'] and problem_data['openlane_pdk'] not in valid_pdks:
                raise ValidationError(f'Row {row_num}: Invalid OpenLane PDK "{problem_data["openlane_pdk"]}". Valid options: {", ".join(valid_pdks)}')
    
    def _process_additional_fields(self, row, problem_data):
        """Process additional fields like groups, types, etc."""
        # Handle group
        group_name = row.get('group', '').strip()
        if group_name:
            from judge.models import ProblemGroup
            try:
                problem_data['group'] = ProblemGroup.objects.get(name=group_name)
            except ProblemGroup.DoesNotExist:
                raise ValidationError(f'Problem group "{group_name}" does not exist')
        
        # Handle problem types
        types_str = row.get('types', '').strip()
        if types_str:
            from judge.models import ProblemType
            type_names = [name.strip() for name in types_str.split(',') if name.strip()]
            types = []
            for type_name in type_names:
                try:
                    types.append(ProblemType.objects.get(name=type_name))
                except ProblemType.DoesNotExist:
                    raise ValidationError(f'Problem type "{type_name}" does not exist')
            problem_data['types'] = types
        
        # Handle allowed languages
        languages_str = row.get('allowed_languages', '').strip()
        if languages_str:
            from judge.models import Language
            language_names = [name.strip() for name in languages_str.split(',') if name.strip()]
            languages = []
            for lang_name in language_names:
                try:
                    languages.append(Language.objects.get(name=lang_name))
                except Language.DoesNotExist:
                    raise ValidationError(f'Language "{lang_name}" does not exist')
            problem_data['allowed_languages'] = languages
        
        # Handle authors, curators, testers
        for field_name in ['authors', 'curators', 'testers', 'banned_users']:
            users_str = row.get(field_name, '').strip()
            if users_str:
                from judge.models import Profile
                usernames = [name.strip() for name in users_str.split(',') if name.strip()]
                users = []
                for username in usernames:
                    try:
                        users.append(Profile.objects.get(user__username=username))
                    except Profile.DoesNotExist:
                        raise ValidationError(f'User "{username}" does not exist for field "{field_name}"')
                problem_data[field_name] = users
        
        # Handle organizations
        orgs_str = row.get('organizations', '').strip()
        if orgs_str:
            from judge.models import Organization
            org_names = [name.strip() for name in orgs_str.split(',') if name.strip()]
            organizations = []
            for org_name in org_names:
                try:
                    organizations.append(Organization.objects.get(name=org_name))
                except Organization.DoesNotExist:
                    raise ValidationError(f'Organization "{org_name}" does not exist')
            problem_data['organizations'] = organizations
        
        # Handle other optional fields
        optional_fields = ['license', 'og_image', 'summary']
        for field in optional_fields:
            value = row.get(field, '').strip()
            if value:
                problem_data[field] = value
        
        # Handle organization private setting
        problem_data['is_organization_private'] = self._parse_boolean(row.get('is_organization_private', 'false'))