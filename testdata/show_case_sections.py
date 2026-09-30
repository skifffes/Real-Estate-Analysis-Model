# -*- coding: utf-8 -*-
"""查看第四章各房企小节实际内容，提取量化要点"""
from pathlib import Path

t = list(Path(r"d:\python\Financial\backend\app\knowledge\documents").glob("imported_64*"))[0].read_text(encoding="utf-8")
i4, iend = t.rfind("第四章：案例房企"), t.rfind("附录：报告原文全文")
seg = t[i4:iend]

for kw in ["恒大集团：产业链传导的", "融创中国：从规模扩张", "碧桂园：从清盘危机",
           "金科股份：司法重整", "世茂集团：境外重组", "阳光城：深度困境"]:
    a = seg.rfind(kw)
    print(f"\n{'='*20} {kw} (位置{a}) {'='*20}")
    print(seg[a:a+500])
