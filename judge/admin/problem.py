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
        (_('Justice'), {'fields': ('banned_users',)}),
        (_('History'), {'fields': ('change_message',)}),
    )
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
                        # 預覽模式：顯示將要創建的題目
                        context = {
                            'form': form,
                            'problems_preview': problems_to_create,
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
        import csv
        
        response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
        response['Content-Disposition'] = 'attachment; filename="sample_problems_with_solutions.csv"'
        
        writer = csv.writer(response)
        
        # 寫入標題行
        headers = [
            'code', 'name', 'description', 'group', 'time_limit', 'memory_limit', 
            'points', 'types', 'authors', 'allowed_languages', 'is_public', 'partial', 'short_circuit',
            'solution_content', 'solution_is_public', 'solution_publish_on', 'solution_authors',
            'translations'
        ]
        writer.writerow(headers)
        
        # 寫入範例資料
        sample_data = [
            [
                'hello_world', 'Hello World', '輸出 Hello World', 'Demo', '1.0', '262144', '100', 
                'Traditional', '', 'Verilog', 'true', 'false', 'false',
                '這是一個最基本的程式設計問題。\n\n**題目要求：**\n輸出字串 "Hello World"\n\n**解題思路：**\n1. 使用基本的輸出語法\n2. 確保輸出正確的字串\n\n**Verilog 解法：**\n```verilog\nmodule hello;\n    initial begin\n        $display("Hello World");\n        $finish;\n    end\nendmodule\n```', 
                'true', '2025-09-01 10:00:00', '',
                'en:Hello World:Output the string Hello World,zh-hant:哈囉世界:輸出字串 Hello World'
            ],
            [
                'add_two_numbers', '兩數相加', '計算兩個整數的和', 'Demo', '2.0', '262144', '150', 
                'Math', '', 'Verilog', 'true', 'true', 'false',
                '這是一個基本的算術問題，需要讀取兩個整數並計算它們的和。\n\n**輸入格式：**\n兩個整數 A 和 B，以空格分隔\n\n**輸出格式：**\n一個整數，表示 A + B 的結果\n\n**解題步驟：**\n1. 讀取兩個整數 A 和 B\n2. 計算 A + B\n3. 輸出結果',
                'true', '2025-09-01 12:00:00', '',
                'en:Add Two Numbers:Calculate the sum of two integers,zh-hant:兩數相加:計算兩個整數的和'
            ],
            [
                'simple_gate', '簡單邏輯門', '實現基本的邏輯門電路', 'Demo', '3.0', '524288', '200', 
                'Implementation', '', 'Verilog', 'true', 'false', 'false',
                '這個問題要求實現基本的邏輯門功能。\n\n**題目描述：**\n給定兩個二進位輸入 A 和 B，實現以下邏輯運算：\n- AND 運算\n- OR 運算\n- XOR 運算\n\n**輸入格式：**\n兩個二進位數字 A 和 B (0 或 1)\n\n**輸出格式：**\n三行，分別輸出 AND、OR、XOR 的結果',
                'true', '2025-09-01 14:00:00', '',
                'en:Simple Logic Gates:Implement basic logic gate operations,zh-hant:簡單邏輯門:實現基本的邏輯門運算'
            ],
        ]
        
        for row in sample_data:
            writer.writerow(row)
            
        return response

    def _create_problem_from_data(self, problem_data):
        """從資料字典創建題目"""
        # 提取多對多關係字段和關聯資料
        types = problem_data.pop('types', [])
        authors = problem_data.pop('authors', [])
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
