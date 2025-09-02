from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


class AllowedEmailDomain(models.Model):
    """
    模型用於管理允許註冊的郵件域名
    """
    domain = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_('Email domain'),
        help_text=_('Allowed email domain for registration (e.g., edu.tw, gmail.com)'),
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                message=_('Enter a valid domain name (e.g., edu.tw, example.com)')
            )
        ]
    )
    
    description = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_('Description'),
        help_text=_('Optional description for this domain')
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is active'),
        help_text=_('Whether this domain is currently allowed for registration')
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at')
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at')
    )
    
    class Meta:
        verbose_name = _('Allowed email domain')
        verbose_name_plural = _('Allowed email domains')
        ordering = ['domain']
    
    def __str__(self):
        return self.domain
    
    @classmethod
    def is_domain_allowed(cls, email):
        """
        檢查給定的電子郵件是否屬於允許的域名
        
        Args:
            email (str): 要檢查的電子郵件地址
            
        Returns:
            bool: 如果電子郵件域名被允許則返回 True，否則返回 False
        """
        if not email or '@' not in email:
            return False
        
        domain = email.split('@')[-1].lower()
        
        # 檢查完整域名匹配
        if cls.objects.filter(domain__iexact=domain, is_active=True).exists():
            return True
        
        # 檢查子域名匹配 (例如: mail.edu.tw 匹配 edu.tw)
        domain_parts = domain.split('.')
        for i in range(len(domain_parts)):
            parent_domain = '.'.join(domain_parts[i:])
            if cls.objects.filter(domain__iexact=parent_domain, is_active=True).exists():
                return True
        
        return False
    
    @classmethod
    def get_allowed_domains_list(cls):
        """
        獲取所有啟用的允許域名列表
        
        Returns:
            list: 啟用的域名列表
        """
        return list(cls.objects.filter(is_active=True).values_list('domain', flat=True))
