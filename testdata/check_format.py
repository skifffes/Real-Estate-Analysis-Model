# -*- coding: utf-8 -*-
from docx import Document

d = Document(r"d:\python\Financial\docs\参赛报告——房地产产业链风险传导分析金融智能体项目（辛苦学长们进一步补充）.docx")
paras = d.paragraphs

def align_str(a):
    try:
        return {0: "LEFT", 1: "CENTER", 2: "RIGHT"}.get(int(a), str(a))
    except Exception:
        return str(a)

print("== cover 0-22 ==")
for i in range(0, 23):
    p = paras[i]
    t = p.text.strip() or "(empty)"
    runs = []
    for r in p.runs[:2]:
        sz = r.font.size.pt if r.font.size else "inh"
        runs.append("sz=%s b=%s" % (sz, r.bold))
    print(i, "[", align_str(p.alignment), "]", t[:36], "; ".join(runs))

print()
print("== headings ==")
for i, p in enumerate(paras[23:], start=23):
    t = p.text.strip()
    if t and (t.startswith(tuple("一二三四五六七八九")) or t.startswith("（") or len(t) < 30):
        bold = p.runs[0].bold if p.runs else None
        print(i, "b=", bold, "[", align_str(p.alignment)[:6], "]", t[:45])