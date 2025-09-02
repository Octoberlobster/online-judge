#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "dmoj.settings")

try:
    import django
except ImportError:
    print("找不到 Django，請在啟用的虛擬環境中執行此腳本。")
    sys.exit(1)

django.setup()

from judge.models import (
    Problem,
    ProblemType,
    ProblemGroup,
    ProblemTranslation,
    Language,
)

def create_problem_with_translations(
    *,
    code: str,
    name: str,
    description: str,
    problem_type_name: str = "Traditional",
    group_name: str = "Demo",
    time_limit: float = 2.0,
    memory_limit: int = 65536,
    points: int = 100,
    name_zh: str | None = None,
    description_zh: str | None = None,
    name_en: str | None = None,
    description_en: str | None = None,
):
    if Problem.objects.filter(code=code).exists():
        print(f"題目 {code} 已存在，略過建立。")
        problem = Problem.objects.get(code=code)
    else:
        problem = Problem(
            code=code,
            name=name,
            description=description,
            time_limit=time_limit,
            memory_limit=memory_limit,
            points=points,
            partial=True,
        )
        group, _ = ProblemGroup.objects.get_or_create(
            name=group_name, defaults={"full_name": group_name}
        )
        problem.group = group
        problem.save()

        ptype, _ = ProblemType.objects.get_or_create(
            name=problem_type_name, defaults={"full_name": problem_type_name}
        )
        problem.types.set([ptype])
        problem.save()
        print(f"✓ 已建立題目：{code} - {name}")

    # 使用短碼 'zh' 與 'en'，避免 Language.key 長度超限
    add_or_update_translation(
        problem=problem,
        language_key="zh",              # 繁體中文（請依你的站台實際 key 調整）
        language_display="Chinese",     # 顯示名稱，隨意
        translated_name=name_zh,
        translated_description=description_zh,
        log_label="繁體中文",
    )
    add_or_update_translation(
        problem=problem,
        language_key="en",
        language_display="English",
        translated_name=name_en,
        translated_description=description_en,
        log_label="英文",
    )
    return problem

def add_or_update_translation(
    *,
    problem: Problem,
    language_key: str,
    language_display: str,
    translated_name: str | None,
    translated_description: str | None,
    log_label: str,
):
    if not translated_name and not translated_description:
        print(f"  - 未提供{log_label}翻譯，略過。")
        return

    # 先嘗試取得既有語言；若沒有則用短碼新增
    lang, _ = Language.objects.get_or_create(
        key=language_key,
        defaults={"name": language_display}
    )

    trans, created = ProblemTranslation.objects.get_or_create(
        problem=problem,
        language=lang,
        defaults={
            "name": translated_name or "",
            "description": translated_description or "",
        },
    )
    if not created:
        changed = False
        if translated_name:
            trans.name = translated_name
            changed = True
        if translated_description:
            trans.description = translated_description
            changed = True
        if changed:
            trans.save()
            print(f"  ↻ 已更新{log_label}翻譯：{trans.name}")
        else:
            print(f"  - {log_label}翻譯已存在且無變更。")
    else:
        print(f"  ✓ 已新增{log_label}翻譯：{trans.name}")

def main():
    print("====")
    print("開始建立 DMOJ 題目（含繁體中文與英文翻譯）")

    create_problem_with_translations(
        code="HELLO001",
        name="Hello World",
        description="""# Problem Description
Write a program that outputs "Hello, World!".

## Input
No input.

## Output
Output "Hello, World!" (without quotes).

## Sample Input
(no input)

## Sample Output
Hello, World!
""",
        time_limit=1.0,
        memory_limit=16384,
        points=10,
        name_zh="你好世界",
        description_zh="""# 題目描述
撰寫一個程式輸出 "Hello, World!"。

## 輸入
無輸入。

## 輸出
輸出 "Hello, World!"（不含引號）。

## 範例輸入
(無)

## 範例輸出
Hello, World!
""",
        name_en="Hello World",
        description_en="""# Problem Description
Write a program that outputs "Hello, World!".

## Input
No input.

## Output
Output "Hello, World!" (without quotes).

## Sample Input
(no input)

## Sample Output
Hello, World!
""",
    )

    print("----------------")

    create_problem_with_translations(
        code="ADD001",
        name="Simple Addition",
        description="""# Problem Description
Given two integers A and B, output A + B.

## Input
Two integers A and B (1 ≤ A, B ≤ 1000).

## Output
Output A + B.

## Sample Input
3 5

## Sample Output
8
""",
        time_limit=1.0,
        memory_limit=32768,
        points=20,
        name_zh="簡單加法",
        description_zh="""# 題目描述
給定兩個整數 A 和 B，輸出 A + B。

## 輸入
兩個整數 A 和 B（1 ≤ A, B ≤ 1000）。

## 輸出
輸出 A + B。

## 範例輸入
3 5

## 範例輸出
8
""",
        name_en="Simple Addition",
        description_en="""# Problem Description
Given two integers A and B, output A + B.

## Input
Two integers A and B (1 ≤ A, B ≤ 1000).

## Output
Output A + B.

## Sample Input
3 5

## Sample Output
8
""",
    )

    print("----------------")

    create_problem_with_translations(
        code="MAX001",
        name="Find Maximum",
        description="""# Problem Description
Given an array of integers, find the maximum value.

## Input
First line: integer n (1 ≤ n ≤ 100)
Second line: n integers (-1000 ≤ each integer ≤ 1000)

## Output
Output the maximum value.

## Sample Input
5
1 3 7 2 5

## Sample Output
7
""",
        time_limit=1.0,
        memory_limit=32768,
        points=30,
        name_zh="尋找最大值",
        description_zh="""# 題目描述
給定一個整數陣列，找出最大值。

## 輸入
第一行：整數 n（1 ≤ n ≤ 100）
第二行：n 個整數（每個整數介於 -1000 到 1000）

## 輸出
輸出最大值。

## 範例輸入
5
1 3 7 2 5

## 範例輸出
7
""",
        name_en="Find Maximum",
        description_en="""# Problem Description
Given an array of integers, find the maximum value.

## Input
First line: integer n (1 ≤ n ≤ 100)
Second line: n integers (-1000 ≤ each integer ≤ 1000)

## Output
Output the maximum value.

## Sample Input
5
1 3 7 2 5

## Sample Output
7
""",
    )

    print("====")
    print("完成。若仍報語言 key 的錯，請先到 Django shell 執行：")
    print("  from judge.models import Language; list(Language.objects.values('id','key','name'))")
    print("確認站台現有的 key，然後把上面腳本中的 'zh' 或 'en' 改成你的實際 key。")

if __name__ == "__main__":
    main()
