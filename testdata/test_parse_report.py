# -*- coding: utf-8 -*-
"""_parse_report 解析容错单测（复现 10-06 报告损坏场景）"""
import sys
sys.path.insert(0, r"d:\python\Financial\backend")

from app.agent.core import RiskAgent

agent = RiskAgent()

# 1. 正常 JSON
ok = agent._parse_report('{"summary": "正常", "risk_level": "高", "risk_score": 70}')
assert ok and ok["risk_score"] == 70, "正常JSON解析失败"
print("[PASS] 正常 JSON")

# 2. 带代码围栏
ok = agent._parse_report('```json\n{"summary": "x", "risk_level": "高"}\n```')
assert ok and ok["risk_level"] == "高"
print("[PASS] 代码围栏")

# 3. 未转义引号（10-06 故障场景复现）
bad = '{"summary": "风险评分显示钢铁均达"极高"等级，核心压力来自收入下降", "risk_level": "高", "risk_score": 78.3}'
r = agent._parse_report(bad)
print(f"[{'PASS' if r is None else 'FAIL'}] 未转义引号 -> {'返回None(触发规则引擎兜底)' if r is None else '仍返回dict'}")

# 4. 尾逗号
ok = agent._parse_report('{"summary": "x", "risk_level": "高",}')
assert ok is not None
print("[PASS] 尾逗号修复")

# 5. 中文引号
ok = agent._parse_report('{"summary": "x", "risk_level": "高"}')
assert ok is not None
print("[PASS] 正常再次确认")

# 6. 空内容
assert agent._parse_report("") is None and agent._parse_report(None) is None
print("[PASS] 空内容 -> None")

print("\n解析容错全部通过")
