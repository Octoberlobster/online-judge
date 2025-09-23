#!/usr/bin/env python
"""
DMOJ 題目批量匯入腳本

基於資料庫表結構設計的 CSV 題目匯入工具，支援：
- 基本題目資訊匯入
- Verilog 特色功能 (波形圖、PPA 分析、F4PGA、OpenLane)
- 解答內容匯入
- 關聯資料處理 (作者、組織、語言限制等)

使用方法：
    python bulk_import_problems.py --csv sample_problems.csv [選項]

CSV 格式說明請參考 BULK_IMPORT_GUIDE.md
"""

import os
import sys
import csv
import argparse
import logging
from datetime import datetime
from typing import Dict, List, Optional

# 設置 Django 環境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')

try:
    import django
    django.setup()
except ImportError:
    print("錯誤: 無法匯入 Django。請確保在 DMOJ 環境中運行此腳本。")
    sys.exit(1)

# Django 設定完成後匯入模型
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dmoj.settings')
django.setup()

from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction
from judge.models import (
    Problem, ProblemType, ProblemGroup, 
    ProblemClarification, Language, Profile, Organization, 
    License, Solution, LanguageLimit
)