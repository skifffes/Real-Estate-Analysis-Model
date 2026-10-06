# -*- coding: utf-8 -*-
"""验证冻结前最后一项：无明确冲击幅度 → 数量模型全部禁止"""
import sys
sys.path.insert(0, r"d:\python\Financial\backend")
from app.agent.core_guards import expected_model, check_tool_allowed

cases = [
    # (问题, 期望 expected_model)
    ("房地产风险怎么看？", "none"),                     # 纯知识 → none
    ("Leontief模型是什么？", "none"),                   # 纯知识 → none
    ("钢铁减产有什么影响？", "none"),                   # 无幅度 → none（反馈点名的场景）
    ("房地产投资下降15%", "leontief"),                  # 明确幅度 → Leontief
    ("钢铁减产10%", "ghosh"),                           # 明确幅度 → Ghosh
    ("房价下降10%", "qualitative"),                     # 房价 → qualitative
    ("钢铁涨价10%", "qualitative"),                     # 价格 → qualitative
]
all_ok = True
for q, exp in cases:
    got = expected_model(q)
    ok = got == exp
    all_ok = all_ok and ok
    print(f"{'OK' if ok else 'FAIL'} {q} -> {got}（期望 {exp}）")

# 无幅度时调用数量模型 → 拦截
a, reason = check_tool_allowed("analyze_industry_chain_impact", "钢铁减产有什么影响？")
print(f"\n无幅度调用数量模型拦截: {a == False} | 理由: {reason[:40]}")
a2, _ = check_tool_allowed("analyze_supply_shock", "房地产风险怎么看？")
print(f"知识问题调用Ghosh拦截: {a2 == False}")

print('\n', '全部通过 ✔' if all_ok and not a and not a2 else '存在FAIL')
