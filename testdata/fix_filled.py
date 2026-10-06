# -*- coding: utf-8 -*-
# 修正 _filled.docx：补简介 + 清标题后缀
import copy
from docx import Document
from docx.shared import Pt

PATH = r"d:\python\Financial\docs\参赛报告——房地产产业链风险传导分析金融智能体项目（辛苦学长们进一步补充）_filled.docx"
doc = Document(PATH)
paras = doc.paragraphs

def insert_after(para, text=None):
    new_p = copy.deepcopy(para._p)
    para._p.addnext(new_p)
    from docx.text.paragraph import Paragraph
    np = Paragraph(new_p, para._parent)
    for r in list(np.runs):
        r._element.getparent().remove(r._element)
    if text is not None:
        np.add_run(text)
    return np

# 1. 简介填充（段落24）
INTRO = [
    "房地产通常被认为具有产业链长、关联行业多、对宏观经济影响范围广等特点。钢铁、水泥、建筑施工、机械设备、家居家电、金融服务等行业，都与房地产开发和交易活动存在不同程度的联系。但“关联行业多”并不等于房地产对所有行业都具有同样强的带动作用；房地产市场发生变化后，风险也不会沿着一条固定路径、以同样速度传导到每一个上下游行业。",
    "本项目从这一问题出发，尝试回答三个更具体的问题：第一，房地产在产业链中的真实关联地位如何，其带动能力是否与通常认知一致；第二，当房地产市场出现需求收缩、上游行业出现供给收缩时，风险分别通过什么路径传导；第三，能否把投入产出模型、行业风险指标、历史案例和大语言模型结合起来，将原本较为复杂的产业链分析转化为普通研究者可以直接使用的分析工具。",
    "项目以北京市投入产出表为主要基础数据，将42部门投入产出表按照房地产产业链分析需要聚合为13个部门，并对2012年、2017年和2023年的产业关联结构进行比较。在需求侧，采用Leontief投入产出模型分析最终需求变化向产业链的传导；在供给侧，采用Ghosh模型分析初始投入收缩向下游部门的关联压力。同时，项目结合收入、债务、现金流和市场需求等因素构建情景风险评分，并通过历史案例和月度指标辅助判断风险传导的阶段和路径。",
    "在研究框架基础上，项目进一步开发了“房地产产业链风险分析智能体”。系统并不让大语言模型直接生成计算结果，而是将知识库检索、Leontief模型、Ghosh模型、风险评分和案例检索封装为独立工具，由服务端判断模型适用条件并完成确定性计算，大语言模型主要承担问题理解、工具调度和结果解释工作。当前系统包含智能问答、风险仪表盘、数据上传和报告中心等功能，能够将产业链分析结果以图谱、评分、阶段判断和结构化报告等形式展示。现有知识库包含60余篇资料并形成8700余个检索切片，案例库整理了9个结构化风险案例。",
    "本项目的重点不是利用人工智能替代产业经济分析，而是将经过验证的研究方法封装成一个可交互、可复现、能够主动说明模型边界的金融分析工具。",
]
i24 = next(i for i, p in enumerate(paras) if p.text.strip() == "（请补充）")
paras[i24].text = INTRO[0]
cur = paras[i24]
for txt in INTRO[1:]:
    cur = insert_after(cur, text=txt)
print("1. intro filled at", i24)

# 2. 清标题后缀“（请补充）”
doc2 = Document(PATH)
count = 0
for p in doc2.paragraphs:
    if "（请补充）" in p.text and not p.text.strip() == "（请补充）":
        for r in p.runs:
            if "（请补充）" in r.text:
                r.text = r.text.replace("（请补充）", "")
                count += 1
print("2. heading suffix cleaned:", count)

doc.save(PATH)
print("saved")