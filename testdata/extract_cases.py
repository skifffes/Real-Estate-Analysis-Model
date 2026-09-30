# -*- coding: utf-8 -*-
"""从素材文档提取6个房企案例 → 追加到 cases.json 结构化案例库"""
import json
import re
from pathlib import Path

src = list(Path(r"d:\python\Financial\backend\app\knowledge\documents").glob("imported_64*"))[0]
t = src.read_text(encoding="utf-8")

# 截取第四章案例部分（正文在目录之后，取最后一次出现）
i4 = t.rfind("第四章：案例房企")
iend = t.rfind("附录：报告原文全文")
seg = t[i4:iend] if i4 > 0 and iend > i4 else t
print(f"案例章节(正文): {i4}~{iend}, {len(seg)}字符\n")


def grab(pattern, text, flags=0):
    m = re.search(pattern, text, flags)
    return m.group(1).strip() if m else ""


# 按房企小节切分
splits = [
    ("case_evergrande", "恒大集团：产业链传导的", "融创中国："),
    ("case_sunac", "融创中国：从规模扩张", "碧桂园：从清盘危机"),
    ("case_countrygarden", "碧桂园：从清盘危机", "金科股份：司法重整"),
    ("case_jinke", "金科股份：司法重整", "世茂集团：境外重组"),
    ("case_shimao", "世茂集团：境外重组", "阳光城：深度困境"),
    ("case_yango", "阳光城：深度困境", "八、案例房企产业链传导"),
]
sections = {}
for cid, start_kw, end_kw in splits:
    a, b = seg.find(start_kw), seg.find(end_kw)
    if a >= 0 and b > a:
        sections[cid] = seg[a:b]
        print(f"{cid}: {b-a}字符")
    else:
        print(f"{cid}: 未找到 ({a},{b})")

CASES_NEW = []
META = {
    "case_evergrande": ("恒大集团债务危机（2021）", 2021, "中国",
        "三道红线+贷款集中度收紧，高杠杆高周转模式难以为继，2021年7月广发银行诉讼引爆流动性危机",
        ["融资端受限", "商票逾期、供应商停止供货", "项目停工、预售资金监管收紧", "美元债违约、理财兑付危机", "上下游企业应收账款与商票减值", "装修装饰/建材供应商重灾区"]),
    "case_sunac": ("融创中国债务重组（2022-2024）", 2022, "中国",
        "并购扩张叠加行业下行，2022年5月美元债利息违约，随后启动境外债重组",
        ["销售回款骤降", "流动性枯竭、公开违约", "孙宏斌让渡控制权引入国资", "境外债重组：债转股+展期", "东方雨虹等供应商追债", "2024年重组完成逐步修复"]),
    "case_countrygarden": ("碧桂园清盘危机与扭亏（2023-2025）", 2023, "中国",
        "2023年8月美元债利息违约触发交叉违约条款，2024年香港清盘呈请，2025年实现扭亏为盈",
        ["销售额断崖式下跌", "境内外债务重组并行", "保交楼压力与资产处置", "供应商账期拉长", "2025年境外债重组落地、经营修复"]),
    "case_jinke": ("金科股份司法重整（2022-2025）", 2022, "中国",
        "2022年商票逾期，重庆首家千亿房企进入司法重整，成为A股首家重整上市房企",
        ["流动性危机爆发", "进入司法重整程序", "引入重整投资人（上海品器联合体）", "债务以房抵债+留债+转股组合清偿", "2025年重整计划执行完毕"]),
    "case_shimao": ("世茂集团境内外债务重组（2022-2024）", 2022, "中国",
        "2022年3月信托违约，此后境内展期与境外重组并行推进",
        ["销售大幅下滑", "信托与非标融资先行违约", "境内债券展期", "境外债重组方案落地", "资产处置回笼资金"]),
    "case_yango": ("阳光城深度困境（2021-2023）", 2021, "中国",
        "2021年三季度商票逾期，流动性枯竭后退市，债务化解进展缓慢的极端样本",
        ["商票逾期连锁反应", "销售归零、债务全面违约", "2023年退市", "化债进展缓慢、多数资产被查封"]),
}
IND_MAP = {"case_evergrande": ["建筑装饰", "建材", "金融业", "建筑业"],
           "case_sunac": ["建筑业", "建材", "金融业"],
           "case_countrygarden": ["建筑业", "建材", "家用电器"],
           "case_jinke": ["专业服务", "金融业", "建筑业"],
           "case_shimao": ["金融业", "建筑业"],
           "case_yango": ["建筑装饰", "金融业"]}
IMPACT = {
    "case_evergrande": "2.4万亿负债敞口，装修装饰与建材供应商应收账款减值重灾",
    "case_sunac": "千亿级债务重组，供应商跨海追债，2024年完成重组",
    "case_countrygarden": "境外债重组关键条款落地，2025年扭亏为盈",
    "case_jinke": "A股首家重整房企，重整计划执行完毕",
    "case_shimao": "境内展期+境外重组并行",
    "case_yango": "退市，化债进展缓慢",
}
LESSON = {
    "case_evergrande": "信用风险沿应付账款/商票渠道向上游传导的速度快于价格渠道",
    "case_sunac": "债务重组中股权让渡与资产处置是恢复产业链信用的关键",
    "case_countrygarden": "大型房企化债是保交楼与稳产业链的政策支点",
    "case_jinke": "司法重整为出险房企产业链风险处置提供市场化范本",
    "case_shimao": "非标融资先于标准化债券违约，是信用恶化的领先信号",
    "case_yango": "销售端失速若叠加融资端枯竭，产业链风险将长期化",
}

for cid, (title, year, region, trigger, transmission) in META.items():
    body = sections.get(cid, "")
    CASES_NEW.append({
        "id": cid,
        "title": title,
        "year": year,
        "region": region,
        "trigger": trigger,
        "transmission": transmission,
        "affected_industries": IND_MAP[cid],
        "peak_impact": IMPACT[cid] + "（详见素材文档第四章）",
        "resolution": grab(r"(\d+\.\d+\s*[^\n]*)", body) or "详见素材文档",
        "lessons": LESSON[cid],
    })

RESOLUTION = {
    "case_evergrande": "2021年底违约后经历两年化债：保交楼专项借款注入、2023年境外债重组方案出台（债转股+展期+以房抵债组合），2024年清盘呈请聆讯多次延期，化债仍在进行",
    "case_sunac": "孙宏斌让渡董事会控制权引入国资战投，2023年11月境外债重组获高票通过（约百亿美元债转股+新票据），2024年完成重组，经营逐步恢复",
    "case_countrygarden": "境内债展期多轮推进，境外债重组方案2025年落地；2025年实现扭亏为盈，成为出险房企修复转折性样本",
    "case_jinke": "2024年法院裁定批准重整计划：上海品器联合体为产业投资人，债务通过现金清偿+以房抵债+留债+转股组合处理，2025年重整计划执行完毕，保交楼同步完成",
    "case_shimao": "境内债多轮展期先行落地，境外债重组方案2024年推进：部分债转股+长年期新票据，配合资产处置回笼资金",
    "case_yango": "2023年因股价连续低于面值退市，多数核心资产被查封，债务化解进展缓慢，成为产业链风险长期化的警示样本",
}

for c in CASES_NEW:
    c["resolution"] = RESOLUTION[c["id"]]

# 追加到 cases.json（原4个案例中，旧恒大案例被更详尽的新版替代）
cdst = Path(r"d:\python\Financial\backend\app\data\cases.json")
cases = json.loads(cdst.read_text(encoding="utf-8"))
cases = [c for c in cases if c["id"] != "case_hd_2021"]  # 去掉旧恒大
exist_ids = {c["id"] for c in cases}
added = [c for c in CASES_NEW if c["id"] not in exist_ids]
cases.extend(added)
cdst.write_text(json.dumps(cases, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"\n案例库: 保留{len(cases)-len(added)}个 + 新增{len(added)}个 = {len(cases)}个")
for c in cases:
    print(" -", c["title"])
