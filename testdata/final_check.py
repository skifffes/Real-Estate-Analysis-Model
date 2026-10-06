# -*- coding: utf-8 -*-
from docx import Document

PATH = r"d:\python\Financial\docs\参赛报告——房地产产业链风险传导分析金融智能体项目（辛苦学长们进一步补充）_filled.docx"
d = Document(PATH)
paras = d.paragraphs
full = "\n".join(p.text for p in paras)

print("请补充残留:", full.count("（请补充）"))
print("插图数:", len(d.inline_shapes))
print("总段落:", len(paras))
i0 = next(i for i, p in enumerate(paras) if p.text.startswith("房地产通常被认为"))
print("简介首段:", paras[i0].text[:45])
print("简介末段:", paras[i0 + 4].text[:45])
for key in ["反常识", "供给约束传导框架", "复合压力测试", "中间使用暴露", "六案例归纳"]:
    print("关键表述:", key, "->", key in full)
# 标题无后缀
for p in paras:
    if p.text.startswith(("五、主要结论", "六、下一步方向", "（四）项目实施过程")):
        print("标题:", p.text[:30])