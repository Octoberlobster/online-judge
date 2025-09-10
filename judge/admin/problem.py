from operator import attrgetter

from django import forms
from django.contrib import admin
from django.db import transaction
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse, reverse_lazy, path
from django.utils import timezone
from django.utils.html import format_html
from django.utils.translation import gettext, gettext_lazy as _, ngettext
from django.contrib import messages
from reversion.admin import VersionAdmin

from judge.models import LanguageLimit, Problem, ProblemClarification, ProblemPointsVote, ProblemTranslation, Profile, \
    Solution
from judge.utils.views import NoBatchDeleteMixin
from judge.widgets import AdminHeavySelect2MultipleWidget, AdminMartorWidget, AdminSelect2MultipleWidget, \
    AdminSelect2Widget, CheckboxSelectMultipleWithSelectAll
from judge.bulk_import_forms import CSVImportForm


class ProblemForm(ModelForm):
    change_message = forms.CharField(max_length=256, label=_('Edit reason'), required=False)

    def __init__(self, *args, **kwargs):
        super(ProblemForm, self).__init__(*args, **kwargs)
        self.fields['authors'].widget.can_add_related = False
        self.fields['curators'].widget.can_add_related = False
        self.fields['testers'].widget.can_add_related = False
        self.fields['banned_users'].widget.can_add_related = False
        self.fields['change_message'].widget.attrs.update({
            'placeholder': gettext('Describe the changes you made (optional)'),
        })

    class Meta:
        widgets = {
            'authors': AdminHeavySelect2MultipleWidget(data_view='profile_select2', attrs={'style': 'width: 100%'}),
            'curators': AdminHeavySelect2MultipleWidget(data_view='profile_select2', attrs={'style': 'width: 100%'}),
            'testers': AdminHeavySelect2MultipleWidget(data_view='profile_select2', attrs={'style': 'width: 100%'}),
            'banned_users': AdminHeavySelect2MultipleWidget(data_view='profile_select2',
                                                            attrs={'style': 'width: 100%'}),
            'organizations': AdminHeavySelect2MultipleWidget(data_view='organization_select2',
                                                             attrs={'style': 'width: 100%'}),
            'types': AdminSelect2MultipleWidget,
            'group': AdminSelect2Widget,
            'description': AdminMartorWidget(attrs={'data-markdownfy-url': reverse_lazy('problem_preview')}),
            #Verilog Settings
            'f4pga_board': AdminSelect2Widget,
            'openlane_pdk': AdminSelect2Widget,
            'f4pga_target_fmax': forms.NumberInput(attrs={'step': '0.1', 'min': '0.1'}),
            'openlane_ppa_score': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'openlane_critical_path_ns': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'openlane_core_area_um2': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'openlane_power_total': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }


class ProblemCreatorListFilter(admin.SimpleListFilter):
    title = parameter_name = 'creator'

    def lookups(self, request, model_admin):
        queryset = Profile.objects.exclude(authored_problems=None).values_list('user__username', flat=True)
        return [(name, name) for name in queryset]

    def queryset(self, request, queryset):
        if self.value() is None:
            return queryset
        return queryset.filter(authors__user__username=self.value())


class LanguageLimitInlineForm(ModelForm):
    class Meta:
        widgets = {'language': AdminSelect2Widget}


class LanguageLimitInline(admin.TabularInline):
    model = LanguageLimit
    fields = ('language', 'time_limit', 'memory_limit')
    form = LanguageLimitInlineForm


class ProblemClarificationForm(ModelForm):
    class Meta:
        widgets = {'description': AdminMartorWidget(attrs={'data-markdownfy-url': reverse_lazy('comment_preview')})}


class ProblemClarificationInline(admin.StackedInline):
    model = ProblemClarification
    fields = ('description',)
    form = ProblemClarificationForm
    extra = 0


class ProblemSolutionForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProblemSolutionForm, self).__init__(*args, **kwargs)
        self.fields['authors'].widget.can_add_related = False

    class Meta:
        widgets = {
            'authors': AdminHeavySelect2MultipleWidget(data_view='profile_select2', attrs={'style': 'width: 100%'}),
            'content': AdminMartorWidget(attrs={'data-markdownfy-url': reverse_lazy('solution_preview')}),
        }


class ProblemSolutionInline(admin.StackedInline):
    model = Solution
    fields = ('is_public', 'publish_on', 'authors', 'content')
    form = ProblemSolutionForm
    extra = 0


class ProblemTranslationForm(ModelForm):
    class Meta:
        widgets = {'description': AdminMartorWidget(attrs={'data-markdownfy-url': reverse_lazy('problem_preview')})}


class ProblemTranslationInline(admin.StackedInline):
    model = ProblemTranslation
    fields = ('language', 'name', 'description')
    form = ProblemTranslationForm
    extra = 0

    def has_permission_full_markup(self, request, obj=None):
        if not obj:
            return True
        return request.user.has_perm('judge.problem_full_markup') or not obj.is_full_markup

    has_add_permission = has_change_permission = has_delete_permission = has_permission_full_markup


class ProblemAdmin(NoBatchDeleteMixin, VersionAdmin):
    fieldsets = (
        (None, {
            'fields': (
                'code', 'name', 'is_public', 'is_manually_managed', 'date', 'authors', 'curators', 'testers',
                'organizations', 'submission_source_visibility_mode', 'is_full_markup',
                'description', 'license',
            ),
        }),
        (_('Social Media'), {'classes': ('collapse',), 'fields': ('og_image', 'summary')}),
        (_('Taxonomy'), {'fields': ('types', 'group')}),
        (_('Points'), {'fields': (('points', 'partial'), 'short_circuit')}),
        (_('Limits'), {'fields': ('time_limit', 'memory_limit')}),
        (_('Language'), {'fields': ('allowed_languages',)}),
        (_('Verilog Settings'), {
            'fields': (
                'enable_waveform',
                'enable_ppa',
                ('f4pga_board', 'f4pga_target_fmax'),
                'openlane_pdk',
                ('openlane_ppa_score', 'openlane_critical_path_ns'),
                ('openlane_core_area_um2', 'openlane_power_total'),
            )
        }),
        (_('Justice'), {'fields': ('banned_users',)}),
        (_('History'), {'fields': ('change_message',)}),
    )
    class Media:
        js = ('admin/js/verilog_settings.js',)
        css = {
            'all': ('admin/css/verilog_settings.css',)
    }

    list_display = ['code', 'name', 'show_authors', 'points', 'is_public', 'show_public']
    ordering = ['code']
    search_fields = ('code', 'name', 'authors__user__username', 'curators__user__username')
    inlines = [LanguageLimitInline, ProblemClarificationInline, ProblemSolutionInline, ProblemTranslationInline]
    list_max_show_all = 1000
    actions_on_top = True
    actions_on_bottom = True
    list_filter = ('is_public', ProblemCreatorListFilter)
    form = ProblemForm
    date_hierarchy = 'date'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('import-csv/', self.admin_site.admin_view(self.import_csv), name='judge_problem_import_csv'),
            path('download-csv-sample/', self.admin_site.admin_view(self.download_csv_sample), name='judge_problem_download_csv_sample'),
        ]
        return custom_urls + urls

    def import_csv(self, request):
        """處理 CSV 匯入的視圖"""
        if request.method == 'POST':
            form = CSVImportForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    problems_to_create = form.process_csv()
                    
                    # 檢查是否是預覽模式
                    if 'preview' in request.POST:
                        # 預覽模式：將字典轉換為物件以便在模板中使用點號語法
                        class PreviewObject:
                            def __init__(self, data_dict):
                                for key, value in data_dict.items():
                                    setattr(self, key, value)
                        
                        problems_preview = [PreviewObject(problem_data) for problem_data in problems_to_create]
                        
                        context = {
                            'form': form,
                            'problems_preview': problems_preview,
                            'title': _('預覽匯入題目'),
                            'opts': self.model._meta,
                            'has_change_permission': self.has_change_permission(request),
                            'is_preview': True,
                        }
                        return render(request, 'admin/judge/problem/import_csv.html', context)
                    
                    # 實際匯入模式
                    created_count = 0
                    with transaction.atomic():
                        for problem_data in problems_to_create:
                            self._create_problem_from_data(problem_data)
                            created_count += 1
                    
                    messages.success(
                        request, 
                        _('成功從 CSV 匯入了 %(count)d 個題目') % {'count': created_count}
                    )
                    return HttpResponseRedirect(reverse('admin:judge_problem_changelist'))
                    
                except Exception as e:
                    messages.error(request, _('匯入失敗: %(error)s') % {'error': str(e)})
        else:
            form = CSVImportForm()
        
        context = {
            'form': form,
            'title': _('匯入題目 CSV'),
            'opts': self.model._meta,
            'has_change_permission': self.has_change_permission(request),
            'is_preview': False,
        }
        return render(request, 'admin/judge/problem/import_csv.html', context)

    def download_csv_sample(self, request):
        """下載範例 CSV 文件"""
        from django.http import HttpResponse
        from django.conf import settings
        import csv
        import os
        
        # 嘗試讀取實際的 sample_problems_with_ppa_complete.csv 檔案
        csv_file_path = os.path.join(settings.BASE_DIR, 'sample_problems_with_ppa_complete.csv')
        
        if os.path.exists(csv_file_path):
            # 如果檔案存在，直接提供檔案內容
            with open(csv_file_path, 'r', encoding='utf-8-sig') as f:
                csv_content = f.read()
            
            response = HttpResponse(csv_content, content_type='text/csv; charset=utf-8-sig')
            response['Content-Disposition'] = 'attachment; filename="sample_problems_with_ppa_complete.csv"'
            return response
        
        # 如果檔案不存在，則生成預設範例
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="sample_problems_with_ppa_complete.csv"'
        
        writer = csv.writer(response)
        
        # 寫入標題行
        headers = [
            'code', 'name', 'description', 'group', 'time_limit', 'memory_limit', 
            'points', 'types', 'authors', 'curators', 'testers', 'allowed_languages', 
            'is_public', 'partial', 'short_circuit', 'is_manually_managed',
            'license', 'og_image', 'summary',
            'banned_users', 'organizations', 'is_organization_private',
            'enable_waveform', 'enable_ppa', 'ppa_maximum_fmax',
            'f4pga_board', 'f4pga_target_fmax',
            'openlane_pdk', 'openlane_ppa_score', 'openlane_critical_path_ns', 
            'openlane_core_area_um2', 'openlane_power_total',
            'solution_content', 'solution_is_public', 'solution_authors',
            'translations'
        ]
        writer.writerow(headers)
        
        # 寫入範例資料 - 完整展示各種匯入情境，避免格式問題
        sample_data = [
            # 1. 基本題目 - 僅功能驗證，無 PPA
            [
                'hello_world', 'Hello World', '輸出 Hello World 字串', 'Demo', '1.0', '262144', '100', 
                'Traditional', '', '', '', 'Verilog', 'true', 'false', 'false', 'false',
                '', '', '這是一個簡單的 Hello World 題目',
                '', '', 'false',
                'false', 'false', '',  # enable_waveform=false, enable_ppa=false, ppa_maximum_fmax=空
                '', '',  # f4pga_board=空, f4pga_target_fmax=空
                '', '', '', '', '',  # 所有 OpenLane 欄位都空
                '這是一個最基本的程式設計問題。\\n\\n**題目要求：**\\n輸出字串 "Hello World"\\n\\n**解題思路：**\\n使用基本的輸出語法確保輸出正確的字串。', 
                'true', '',
                'en:Hello World:Output the string Hello World|zh-hant:哈囉世界:輸出字串 Hello World'
            ],
            # 2. 波形檢視題目 - 啟用波形但無 PPA
            [
                'logic_gates', '基本邏輯閘', '實作基本邏輯閘電路', 'Demo', '2.0', '262144', '150', 
                'Traditional', '', '', '', 'Verilog', 'true', 'true', 'false', 'false',
                '', '', '基本邏輯閘設計，可觀察波形',
                '', '', 'false',
                'true', 'false', '',  # enable_waveform=true, enable_ppa=false, ppa_maximum_fmax=空
                '', '',  # f4pga_board=空, f4pga_target_fmax=空
                '', '', '', '', '',  # 所有 OpenLane 欄位都空
                '設計基本的邏輯閘電路，可以觀察波形變化。\\n\\n**題目要求：**\\n- 實作 AND、OR、XOR 邏輯閘\\n- 輸入：兩個 1-bit 信號\\n- 輸出：三個 1-bit 信號\\n\\n**特色：**\\n- 啟用波形檢視功能\\n- 適合觀察邏輯運算的時序特性', 
                'true', '',
                'en:Logic Gates:Basic logic gate implementation|zh-hant:邏輯閘:基本邏輯閘實作'
            ],
            # 3. 純 F4PGA 題目 - 智能判斷會自動啟用 F4PGA
            [
                'fpga_counter', 'FPGA 計數器設計', '使用 F4PGA 的計數器電路', 'Demo', '3.0', '524288', '200', 
                'Implementation', '', '', '', 'Verilog', 'true', 'true', 'false', 'false',
                '', '', 'F4PGA FPGA 設計挑戰',
                '', '', 'false',
                'true', 'true', '120.0',  # enable_waveform=true, enable_ppa=true, ppa_maximum_fmax=120.0
                'basys3', '100.0',  # f4pga_board=basys3, f4pga_target_fmax=100.0 (智能判斷：啟用 F4PGA)
                '', '', '', '', '',  # 所有 OpenLane 欄位都空 (智能判斷：不啟用 OpenLane)
                'F4PGA FPGA 計數器設計，目標 Basys3 開發板。\\n\\n**設計要求：**\\n- 實作 8-bit 上下計數器\\n- 目標開發板：Basys3\\n- F4PGA 要求：目標頻率 ≥100 MHz\\n- 全域頻率限制：≤120 MHz\\n\\n**智能判斷：**\\n因為填入了 f4pga_board 和 f4pga_target_fmax，系統會自動啟用 F4PGA 功能。', 
                'true', '',
                'en:FPGA Counter:F4PGA counter design for Basys3|zh-hant:FPGA計數器:Basys3的F4PGA計數器設計'
            ],
            # 4. 純 OpenLane 題目 - 智能判斷會自動啟用 OpenLane  
            [
                'asic_alu', 'ASIC ALU 設計', '使用 OpenLane 的 ALU 電路', 'Demo', '5.0', '1048576', '300', 
                'Implementation', '', '', '', 'Verilog', 'true', 'true', 'false', 'true',
                '', '', 'OpenLane ASIC 設計挑戰',
                '', '', 'false',
                'true', 'true', '150.0',  # enable_waveform=true, enable_ppa=true, ppa_maximum_fmax=150.0
                '', '',  # f4pga_board=空, f4pga_target_fmax=空 (智能判斷：不啟用 F4PGA)
                'sky130A', '80.0', '10.0', '2000.0', '50.0',  # 填入 OpenLane 欄位 (智能判斷：啟用 OpenLane)
                'OpenLane ASIC ALU 設計，需要滿足嚴格的 PPA 約束。\\n\\n**設計要求：**\\n- 實作 8-bit 算術邏輯單元\\n- 全域頻率限制：≤150 MHz\\n\\n**OpenLane PPA 約束：**\\n- PDK：sky130A\\n- PPA 分數：≥80\\n- 關鍵路徑：≤10 ns\\n- 核心面積：≤2000 μm²\\n- 總功耗：≤50 mW\\n\\n**智能判斷：**\\n因為填入了 OpenLane 相關欄位，系統會自動啟用 OpenLane 功能。', 
                'false', '',
                'en:ASIC ALU:OpenLane ASIC ALU design|zh-hant:ASIC算術邏輯單元:OpenLane ASIC ALU設計'
            ],
            # 5. 混合 PPA 題目 - 同時啟用 F4PGA 和 OpenLane
            [
                'hybrid_processor', '混合處理器設計', '跨平台處理器設計', 'Demo', '8.0', '2097152', '500', 
                'Implementation', '', '', '', 'Verilog', 'true', 'true', 'false', 'true',
                '', '', '同時支援 FPGA 和 ASIC 的處理器設計',
                '', '', 'false',
                'true', 'true', '200.0',  # enable_waveform=true, enable_ppa=true, ppa_maximum_fmax=200.0
                'arty_a7_100t', '150.0',  # f4pga_board=arty_a7_100t, f4pga_target_fmax=150.0 (智能判斷：啟用 F4PGA)
                'sky130B', '85.0', '8.0', '3000.0', '60.0',  # 同時填入 OpenLane 欄位 (智能判斷：同時啟用 OpenLane)
                '混合 PPA 分析的處理器核心設計。\\n\\n**雙重 PPA 約束：**\\n\\n**F4PGA (FPGA)：**\\n- 開發板：Arty A7-100T\\n- 目標頻率：≥150 MHz\\n\\n**OpenLane (ASIC)：**\\n- PDK：sky130B\\n- PPA 分數：≥85\\n- 關鍵路徑：≤8 ns\\n- 核心面積：≤3000 μm²\\n- 總功耗：≤60 mW\\n\\n**全域限制：**\\n- 最大頻率：≤200 MHz\\n\\n**智能判斷：**\\n因為同時填入了 F4PGA 和 OpenLane 欄位，系統會啟用完整的 PPA 分析功能。', 
                'true', '',
                'en:Hybrid Processor:Cross-platform processor design|zh-hant:混合處理器:跨平台處理器設計'
            ],
            # 6. 數學題目範例 - 非 Verilog 題目
            [
                'add_numbers', '兩數相加', '計算兩個整數的和', 'Demo', '1.0', '262144', '100', 
                'Math', '', '', '', 'C,Python', 'true', 'true', 'false', 'false',
                '', '', '基本的數學運算題目',
                '', '', 'false',
                'false', 'false', '',  # 非 Verilog 題目，所有 Verilog 欄位都不啟用
                '', '',
                '', '', '', '', '',
                '這是一個基本的算術問題。\\n\\n**輸入格式：**\\n兩個整數 A 和 B，以空格分隔\\n\\n**輸出格式：**\\n一個整數，表示 A + B 的結果\\n\\n**範例：**\\n輸入：3 5\\n輸出：8\\n\\n**解題步驟：**\\n1. 讀取兩個整數 A 和 B\\n2. 計算 A + B\\n3. 輸出結果', 
                'true', '',
                'en:Add Two Numbers:Calculate the sum of two integers|zh-hant:兩數相加:計算兩個整數的和'
            ]
        ]
        
        for row in sample_data:
            writer.writerow(row)
            
        return response

    def _create_problem_from_data(self, problem_data):
        """從資料字典創建題目"""
        # 提取多對多關係字段和關聯資料
        types = problem_data.pop('types', [])
        authors = problem_data.pop('authors', [])
        curators = problem_data.pop('curators', [])
        testers = problem_data.pop('testers', [])
        banned_users = problem_data.pop('banned_users', [])
        organizations = problem_data.pop('organizations', [])
        allowed_languages = problem_data.pop('allowed_languages', [])
        solution_data = problem_data.pop('solution', None)
        translations_data = problem_data.pop('translations', None)

        # 創建題目
        problem = Problem.objects.create(**problem_data)

        # 設置多對多關係
        if types:
            problem.types.set(types)
        if authors:
            problem.authors.set(authors)
        if curators:
            problem.curators.set(curators)
        if testers:
            problem.testers.set(testers)
        if banned_users:
            problem.banned_users.set(banned_users)
        if organizations:
            problem.organizations.set(organizations)
        if allowed_languages:
            problem.allowed_languages.set(allowed_languages)
        else:
            # 如果沒有指定語言，設置所有可用語言
            from judge.models import Language
            problem.allowed_languages.set(Language.objects.all())

        # 創建題解
        if solution_data:
            solution_authors = solution_data.pop('authors', [])
            solution = Solution.objects.create(
                problem=problem,
                **solution_data
            )
            if solution_authors:
                solution.authors.set(solution_authors)

        # 創建翻譯
        if translations_data:
            for translation_data in translations_data:
                ProblemTranslation.objects.create(
                    problem=problem,
                    **translation_data
                )

        return problem

    def get_actions(self, request):
        actions = super(ProblemAdmin, self).get_actions(request)

        # 加入 CSV 匯入動作
        func, name, desc = self.get_action('csv_import_action')
        actions[name] = (func, name, desc)

        if request.user.has_perm('judge.change_public_visibility'):
            func, name, desc = self.get_action('make_public')
            actions[name] = (func, name, desc)

            func, name, desc = self.get_action('make_private')
            actions[name] = (func, name, desc)

        func, name, desc = self.get_action('update_publish_date')
        actions[name] = (func, name, desc)

        return actions

    def csv_import_action(self, request, queryset):
        """CSV 匯入動作 - 重定向到匯入頁面"""
        from django.shortcuts import redirect
        return redirect('admin:judge_problem_import_csv')
    
    csv_import_action.short_description = _('匯入 CSV 文件')

    def get_readonly_fields(self, request, obj=None):
        fields = self.readonly_fields
        if not request.user.has_perm('judge.change_public_visibility'):
            fields += ('is_public',)
        if not request.user.has_perm('judge.change_manually_managed'):
            fields += ('is_manually_managed',)
        if not request.user.has_perm('judge.problem_full_markup'):
            fields += ('is_full_markup',)
            if obj and obj.is_full_markup:
                fields += ('description',)
        return fields

    def show_authors(self, obj):
        return ', '.join(map(attrgetter('user.username'), obj.authors.all()))

    show_authors.short_description = _('Authors')

    def show_public(self, obj):
        return format_html('<a href="{1}">{0}</a>', gettext('View on site'), obj.get_absolute_url())

    show_public.short_description = ''

    def _rescore(self, request, problem_id):
        from judge.tasks import rescore_problem
        transaction.on_commit(rescore_problem.s(problem_id).delay)

    def update_publish_date(self, request, queryset):
        count = queryset.update(date=timezone.now())
        self.message_user(request, ngettext("%d problem's publish date successfully updated.",
                                            "%d problems' publish date successfully updated.",
                                            count) % count)

    update_publish_date.short_description = _('Set publish date to now')

    def make_public(self, request, queryset):
        count = queryset.update(is_public=True)
        for problem_id in queryset.values_list('id', flat=True):
            self._rescore(request, problem_id)
        self.message_user(request, ngettext('%d problem successfully marked as public.',
                                            '%d problems successfully marked as public.',
                                            count) % count)

    make_public.short_description = _('Mark problems as public')

    def make_private(self, request, queryset):
        count = queryset.update(is_public=False)
        for problem_id in queryset.values_list('id', flat=True):
            self._rescore(request, problem_id)
        self.message_user(request, ngettext('%d problem successfully marked as private.',
                                            '%d problems successfully marked as private.',
                                            count) % count)

    make_private.short_description = _('Mark problems as private')

    def get_queryset(self, request):
        return Problem.get_editable_problems(request.user).prefetch_related('authors__user').distinct()

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return request.user.has_perm('judge.edit_own_problem')
        return obj.is_editable_by(request.user)

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == 'allowed_languages':
            kwargs['widget'] = CheckboxSelectMultipleWithSelectAll()
        return super(ProblemAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

    def get_form(self, *args, **kwargs):
        form = super(ProblemAdmin, self).get_form(*args, **kwargs)
        form.base_fields['authors'].queryset = Profile.objects.all()
        return form

    def save_model(self, request, obj, form, change):
        # `organizations` will not appear in `cleaned_data` if user cannot edit it
        if form.changed_data and 'organizations' in form.changed_data:
            obj.is_organization_private = bool(form.cleaned_data['organizations'])
        super(ProblemAdmin, self).save_model(request, obj, form, change)
        if (
            form.changed_data and
            any(f in form.changed_data for f in ('is_public', 'organizations', 'points', 'partial'))
        ):
            self._rescore(request, obj.id)

    def construct_change_message(self, request, form, *args, **kwargs):
        if form.cleaned_data.get('change_message'):
            return form.cleaned_data['change_message']
        return super(ProblemAdmin, self).construct_change_message(request, form, *args, **kwargs)


class ProblemPointsVoteAdmin(admin.ModelAdmin):
    list_display = ('points', 'voter', 'linked_problem', 'vote_time')
    search_fields = ('voter__user__username', 'problem__code', 'problem__name')
    readonly_fields = ('voter', 'problem', 'vote_time')

    def get_queryset(self, request):
        return ProblemPointsVote.objects.filter(problem__in=Problem.get_editable_problems(request.user))

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        if obj is None:
            return request.user.has_perm('judge.edit_own_problem')
        return obj.problem.is_editable_by(request.user)

    def lookup_allowed(self, key, value):
        return super().lookup_allowed(key, value) or key in ('problem__code',)

    def linked_problem(self, obj):
        link = reverse('problem_detail', args=[obj.problem.code])
        return format_html('<a href="{0}">{1}</a>', link, obj.problem.name)
    linked_problem.short_description = _('problem')
    linked_problem.admin_order_field = 'problem__name'
