# -*- coding: utf-8 -*-
from docx import Document
PATH = r"d:\python\Financial\docs\参赛报告——房地产产业链风险传导分析金融智能体项目（辛苦学长们进一步补充）_filled.docx"
d = Document(PATH)
for i, p in enumerate(d.paragraphs):
    t = p.text
    if "相比" in t or "通用大模型" in t:
        print(i, "|", t[:80])