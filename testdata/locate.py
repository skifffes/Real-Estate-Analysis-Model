# -*- coding: utf-8 -*-
from docx import Document

d = Document(r"d:\python\Financial\docs\参赛报告——房地产产业链风险传导分析金融智能体项目（辛苦学长们进一步补充）_filled.docx")
paras = d.paragraphs

for i, p in enumerate(paras):
    if "请补充" in p.text:
        print("RESIDUAL", i, "|", p.text[:60])

i0 = None
for i, p in enumerate(paras):
    if "参赛项目简介" in p.text:
        i0 = i
        break
print("intro at", i0)
for j in range(i0, i0 + 9):
    print(j, "|", paras[j].text[:55])