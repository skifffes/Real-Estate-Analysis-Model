# -*- coding: utf-8 -*-
from docx import Document

d = Document(r"d:\python\Financial\docs\参赛报告——房地产产业链风险传导分析金融智能体项目（辛苦学长们进一步补充）_filled.docx")
paras = d.paragraphs
full = "\n".join(p.text for p in paras)

print("请补充 残留数:", full.count("（请补充）"))
print("插图数:", len(d.inline_shapes))
print("段落数:", len(paras))

# 结构完整性
for key in ["参赛项目简介", "一、选题背景", "三、Leontief", "四、实验方法", "五、主要结论及不足", "六、下一步方向", "九、结语" ]:
    pass
for key in ["参赛项目简介", "一、选题背景", "二、产业关联分析模型综述", "三、Leontief", "四、实验方法及演示", "五、主要结论及不足", "六、下一步方向"]:
    print("章节存在:", key, "->", key in full)

# 新增内容抽查
print()
print("简介首段:", paras[[i for i,p in enumerate(paras) if p.text.startswith("房地产通常被认为")][0]].text[:50])
for key in ["反常识", "供给约束", "复合压力测试", "情景测算"]:
    print("关键表述:", key, "->", key in full)