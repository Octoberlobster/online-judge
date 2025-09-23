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
    extra = 1

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
    change_list_template = 'admin/judge/problem/change_list.html'

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
                                    if key == 'translations' and isinstance(value, list):
                                        # 特別處理翻譯資料
                                        translation_objects = []
                                        for trans_data in value:
                                            trans_obj = type('TranslationPreview', (), {})()
                                            trans_obj.language = trans_data.get('language', '')
                                            trans_obj.name = trans_data.get('name', '')
                                            trans_obj.description = trans_data.get('description', '')
                                            translation_objects.append(trans_obj)
                                        setattr(self, key, translation_objects)
                                    elif key == 'clarifications' and isinstance(value, list):
                                        # 特別處理澄清說明資料
                                        clarification_objects = []
                                        for clar_data in value:
                                            clar_obj = type('ClarificationPreview', (), {})()
                                            clar_obj.description = clar_data.get('description', '')
                                            clarification_objects.append(clar_obj)
                                        setattr(self, key, clarification_objects)
                                    else:
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
        
        # 嘗試讀取新的修正版範例檔案
        csv_file_path = os.path.join(settings.BASE_DIR, 'enhanced_sample_problems.csv')
        
        if os.path.exists(csv_file_path):
            # 如果檔案存在，直接提供檔案內容
            with open(csv_file_path, 'r', encoding='utf-8-sig') as f:
                csv_content = f.read()
            
            response = HttpResponse(csv_content, content_type='text/csv; charset=utf-8-sig')
            response['Content-Disposition'] = 'attachment; filename="enhanced_sample_problems.csv"'
            return response
        
        
        # 如果檔案不存在，則生成基本範例
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="enhanced_sample_problems.csv"'
        
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
            'translation_en_name', 'translation_en_description',
            'translation_zh_hant_name', 'translation_zh_hant_description',
            'clarifications', 'language_limits', 'is_full_markup'
        ]
        writer.writerow(headers)
        
        # 寫入實用的範例資料
        sample_data = [
            [
                'hello_world', 'Hello World', '輸出 Hello World 字串到標準輸出', 'Demo', '1.0', '262144', '100', 
                'Traditional', '', '', '', '', 'true', 'false', 'false', 'false',
                'CC0-1.0', '', '這是一個簡單的 Hello World 入門題目',
                '', '', 'false',
                'true', 'false', '',
                '', '',
                '', '', '', '', '',
                '這是一個基礎的 Verilog 模組範例，用於輸出固定字串。\\n\\nmodule hello_world;\\ninitial begin\\n    $display("Hello World");\\n    $finish;\\nend\\nendmodule', 'true', '',
                'Hello World', 'Output the string Hello World to standard output',
                'Hello World', '輸出 Hello World 字串到標準輸出',
                '請確保輸出格式完全正確，包括大小寫;不要忘記在輸出後結束模擬',
                '', 'false'
            ],
            [
                'fpga_counter', 'FPGA 8位元計數器', '設計一個8位元二進制計數器，支援時鐘和重置信號', 'Demo', '3.0', '524288', '200', 
                'Implementation', '', '', '', '', 'true', 'true', 'false', 'false',
                '', '', '使用 F4PGA 工具鏈的 FPGA 設計挑戰',
                '', '', 'false',
                'true', 'true', '120.0',
                'basys3', '100.0',
                '', '', '', '', '',
                '設計一個8位元計數器模組：\\n\\nmodule counter_8bit(\\n    input clk,\\n    input reset,\\n    output [7:0] count\\n);\\n\\nreg [7:0] count_reg;\\n\\nalways @(posedge clk or posedge reset) begin\\n    if (reset)\\n        count_reg <= 8\'b0;\\n    else\\n        count_reg <= count_reg + 1;\\nend\\n\\nassign count = count_reg;\\n\\nendmodule', 'true', '',
                'FPGA 8-bit Counter', 'Design an 8-bit binary counter with clock and reset signals',
                'FPGA 8位元計數器', '設計一個8位元二進制計數器，支援時鐘和重置信號',
                '計數器必須支援同步重置功能;設計目標頻率為100MHz;請注意時序約束的設定',
                '', 'false'
            ],
            [
                'asic_alu', 'ASIC 算術邏輯單元', '設計一個4位元ALU，支援加法、減法、AND、OR運算', 'Demo', '2.0', '512000', '150',
                'Implementation', '', '', '', '', 'true', 'true', 'false', 'true',
                '', '', '使用 OpenLane 流程的 ASIC 設計挑戰',
                '', '', 'false',
                'true', 'true', '200.0',
                '', '',
                'sky130A', '75.0', '8.5', '1500.0', '35.0',
                '設計一個4位元ALU模組：\\n\\nmodule alu_4bit(\\n    input [3:0] a, b,\\n    input [1:0] op,\\n    output [3:0] result,\\n    output carry_out\\n);\\n\\n// 運算碼：00=ADD, 01=SUB, 10=AND, 11=OR\\n\\nendmodule', 'false', '',
                'ASIC ALU', 'Design a 4-bit ALU supporting addition, subtraction, AND, OR operations',
                'ASIC 算術邏輯單元', '設計一個4位元ALU，支援加法、減法、AND、OR運算',
                '請實作所有四種運算功能;注意進位輸出的正確性;考慮功耗和面積最佳化',
                '', 'false'
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
        clarifications_data = problem_data.pop('clarifications', None)
        language_limits_data = problem_data.pop('language_limits', None)

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

        # 創建澄清說明
        if clarifications_data:
            for clarification_data in clarifications_data:
                ProblemClarification.objects.create(
                    problem=problem,
                    **clarification_data
                )

        # 創建語言限制
        if language_limits_data:
            for limit_data in language_limits_data:
                LanguageLimit.objects.create(
                    problem=problem,
                    **limit_data
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
