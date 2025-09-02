from django.db import models
from django.utils.translation import gettext_lazy as _


class CSVImportHelper(models.Model):
    """
    這是一個虛擬模型，用於在管理員介面中顯示 CSV 匯入功能
    不會實際創建資料庫表格
    """
    
    class Meta:
        managed = False  # 不會創建資料庫表格
        verbose_name = _('CSV 匯入')
        verbose_name_plural = _('CSV 匯入')
        app_label = 'judge'
