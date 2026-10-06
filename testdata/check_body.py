# -*- coding: utf-8 -*-
from docx import Document

d = Document(r"d:\python\Financial\docs\参赛报告——房地产产业链风险传导分析金融智能体项目（辛苦学长们进一步补充）.docx")
paras = d.paragraphs

# 已写好的正文部分：44-94
print("== body 44-94 (style|bold|text80) ==")
for i in range(44, 95):
    p = paras[i]
    t = p.text.strip()
    if not t:
        continue
    bold = p.runs[0].bold if p.runs else None
    print(i, "b=", bold, "|", t[:80])

print()
print("== 95-126 tail ==")
for i in range(95, 127):
    p = paras[i]
    t = p.text.strip()
    if not t:
        continue
    print(i, "|", t[:70])