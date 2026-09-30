# -*- coding: utf-8 -*-
"""查看素材文档中房企案例章节的详细内容"""
from pathlib import Path

t = list(Path(r"d:\python\Financial\backend\app\knowledge\documents").glob("imported_64*"))[0].read_text(encoding="utf-8")

# 定位"二、出险房企案例分析报告"章节
i = t.find("二、出险房企案例分析报告")
if i > 0:
    seg = t[i:i + 2500]
    print("=== 房企案例章节内容 ===")
    print(seg)
