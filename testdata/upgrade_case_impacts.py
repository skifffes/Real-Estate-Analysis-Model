# -*- coding: utf-8 -*-
"""用素材文档第四章的真实量化数据升级案例 peak_impact/lessons"""
import json
from pathlib import Path

cdst = Path(r"d:\python\Financial\backend\app\data\cases.json")
cases = json.loads(cdst.read_text(encoding="utf-8"))

UP = {
    "case_evergrande": {
        "peak_impact": "总负债2.44万亿（净资产-5991亿）；应付账款与票据6669亿波及上下游；仅43亿可支配现金；200城超2000亿合同负债对应未交付房源",
        "lessons": "信用风险沿商票/应付账款渠道向上游传导快于价格渠道；中泰测算：银行涉房债务违约率需达30%才侵蚀2021年净利，系统性传染有限",
    },
    "case_sunac": {
        "peak_impact": "累计被执行超456亿元；营收较峰值缩水80%+；2025年完成境内外全部债务重组（首家大型房企）",
        "lessons": "债务重组成功缓解供应商坏账压力，但对长三角、西部建筑建材供应商的区域性冲击仍在消化",
    },
    "case_countrygarden": {
        "peak_impact": "境外债减债116亿美元（约850亿）；有息负债降至1480亿（-42%）；总负债7679亿（-2167亿）；3年保交楼115万套",
        "lessons": "深耕三四线，出险对下沉市场建筑/建材/家居供应商冲击面广；2025年扭亏释放头部房企出清信号",
    },
    "case_jinke": {
        "peak_impact": "投资人注资26.28亿（上海品器+长城资产+川发基金）；模拟清算清偿率仅3.02%，重整后普通债权综合清偿率22.36%",
        "lessons": "全国首家千亿级房企司法重整成功；AMC介入体现金融+产业协同化解风险的思路；对西南建筑建材供应商影响显著",
    },
    "case_shimao": {
        "peak_impact": "境外债减债约115亿美元；境内贷款展期约238亿元（最长至2035年）",
        "lessons": "深耕长三角，出险对高端住宅产业链（精装修/高端建材）影响较大；资产变卖是主要化债手段",
    },
    "case_yango": {
        "peak_impact": "净资产-271亿元资不抵债；到期未付债务约666亿元；十万套未交付房源、资金缺口约300亿元",
        "lessons": "六案例中唯一未形成系统性重组方案（躺平型）；下游家居家电需求长期缺失，供应商坏账风险最高",
    },
}
for c in cases:
    if c["id"] in UP:
        c["peak_impact"] = UP[c["id"]]["peak_impact"]
        c["lessons"] = UP[c["id"]]["lessons"]
        c["resolution"] = c["resolution"].replace("（详见素材文档第四章）", "").strip()

cdst.write_text(json.dumps(cases, ensure_ascii=False, indent=2), encoding="utf-8")
for c in cases:
    if c["id"] in UP:
        print(f"✓ {c['title']}")
        print(f"  影响: {c['peak_impact'][:80]}")
