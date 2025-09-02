from django.contrib import admin
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from judge.models.csv_import_helper import CSVImportHelper


@admin.register(CSVImportHelper)
class CSVImportHelperAdmin(admin.ModelAdmin):
    """
    CSV 匯入助手管理員類別
    """
    
    def changelist_view(self, request, extra_context=None):
        """
        重寫列表檢視，直接重定向到 CSV 匯入頁面
        """
        return redirect('admin:judge_problem_import_csv')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def has_view_permission(self, request, obj=None):
        return request.user.has_perm('judge.add_problem')
