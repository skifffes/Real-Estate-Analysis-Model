# -*- coding: utf-8 -*-
# 复现 LLM 模式光伏的 finalize 链路（不调LLM，手工构造）
import sys
sys.path.insert(0, r"d:\python\Financial\backend")
from app.agent.core import RiskAgent

agent = RiskAgent()

# 模拟 LLM 输出（含自编评分）+ 无 impact + 无 cases（光伏场景案例被滤空）
llm_report = {
    "summary": "光伏组件减产15%...综合风险评分 55",
    "risk_level": "中",
    "risk_score": 55,
    "affected_industries": [{"industry": "硅片", "impact_pct": -12.0, "risk_score": 62, "risk_level": "重度"}],
}
final = agent.finalize_report(llm_report, None, [])
print("risk_score after finalize:", final.get("risk_score"))
print("affected_industries:", final.get("affected_industries"))
print("industry_scores:", final.get("industry_scores"))
print("summary tail:", final.get("summary", "")[-60:])