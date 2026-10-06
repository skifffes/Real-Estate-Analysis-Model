# -*- coding: utf-8 -*-
from docx import Document
PATH = r"d:\python\Financial\docs\参赛报告——房地产产业链风险传导分析金融智能体项目（辛苦学长们进一步补充）_filled.docx"
d = Document(PATH)
paras = d.paragraphs
full = "\n".join(p.text for p in paras)
print("请补充残留:", full.count("（请补充）"))
print("插图:", len(d.inline_shapes), "| 段落:", len(paras))
for key in ["复合压力测试", "B = D^(-1) Z", "0.7303", "中间使用暴露", "供给约束", "不篡改量化情景参数", "反常识"]:
    print("关键表述:", key, "->", key in full)
print()
print("== 章节结构 ==")
for i, p in enumerate(paras):
    t = p.text.strip()
    if t[:2] in ("一、","二、","三、","四、","五、","六、") or t == "参赛项目简介":
        print(" ", t[:32])