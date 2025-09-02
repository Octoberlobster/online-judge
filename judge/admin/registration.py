from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from judge.models.registration import AllowedEmailDomain


@admin.register(AllowedEmailDomain)
class AllowedEmailDomainAdmin(admin.ModelAdmin):
    list_display = ('domain', 'description', 'is_active', 'is_active_display', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at', 'updated_at')
    search_fields = ('domain', 'description')
    list_editable = ('is_active',)
    ordering = ('domain',)
    
    fieldsets = (
        (None, {
            'fields': ('domain', 'description', 'is_active')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def is_active_display(self, obj):
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ {}</span>',
                _('Active')
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ {}</span>',
                _('Inactive')
            )
    
    is_active_display.short_description = _('Status')
    is_active_display.admin_order_field = 'is_active'
    
    def get_queryset(self, request):
        return super().get_queryset(request)
    
    def save_model(self, request, obj, form, change):
        # 確保域名是小寫的
        obj.domain = obj.domain.lower()
        super().save_model(request, obj, form, change)
    
    class Meta:
        verbose_name = _('Allowed email domain')
        verbose_name_plural = _('Allowed email domains')
