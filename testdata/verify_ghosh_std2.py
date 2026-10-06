# -*- coding: utf-8 -*-
"""验证标准 Ghosh (I-B)^(-1)：API 结果与独立重算对照 + Canonical Scenario 参数覆盖"""
import json
import sys
import urllib.request

# ============ 第一部分：独立重算 ============
sys.path.insert(0, r"d:\python\Financial\backend")
import numpy as np
from app.models import input_output as io

Z = io.A * io.X_BASE[None, :]
D = np.diag(io.X_BASE)
B = np.linalg.inv(D) @ Z            # B = D⁻¹Z
G = np.linalg.inv(np.eye(io.N) - B)
j = io.SECTOR_NAMES.index("钢铁")
VA = io.X_BASE - (io.A * io.X_BASE[None, :]).sum(axis=0)
dV = np.zeros(io.N)
dV[j] = -0.10 * VA[j]
dX_ref = dV @ G
print(f"独立重算: ρ(B)={max(abs(np.linalg.eigvals(B))):.6f} | (I-B)条件数={np.linalg.cond(np.eye(io.N)-B):.2f}")
print(f"独立重算 钢铁增加值-10%: 总变动 {dX_ref.sum():.1f} 亿元")

# API 结果
req = urllib.request.Request('http://localhost:8000/api/chat',
    data=json.dumps({'question': '钢铁减产10%对哪些行业影响最大'}).encode(),
    headers={'Content-Type': 'application/json'})
r = json.load(urllib.request.urlopen(req, timeout=180))
imp = r.get('impact', {})
print(f"\nAPI: 模型={imp.get('model','')[:50]}")
print(f"API: 总变动 {imp.get('total_output_change_yi')} 亿元 | 供给乘数 {imp.get('supply_multiplier')}")
print(f"工具轨迹: {[t['tool'] for t in r.get('tool_trace', [])][:3]}")
diff = abs(abs(imp.get('total_output_change_yi', 0)) - abs(dX_ref.sum()))
print(f"\n独立重算 vs API 差异: {diff:.1f} 亿元", "✔ 一致" if diff < 5 else "✘ 不一致")

# ============ 第二部分：Canonical Scenario 参数覆盖验证 ============
print("\n" + "=" * 50)
print("Canonical Scenario 验证（LLM 错误参数被服务端解析值覆盖）")
from app.agent.tools import execute_tool

QUESTION = "房地产投资下降15%有什么影响？"

r1 = execute_tool("analyze_industry_chain_impact",
                  {"shock_percent": 20, "direction": "下降"},   # LLM 错误提交 20%
                  question=QUESTION)
p1 = r1["scenario"]
print("1. LLM提交20% -> 引擎实际幅度:", "15.0%（覆盖成功）" if ("15.0%" in p1 and "20%" not in p1) else f"✘ {p1[:50]}")

r2 = execute_tool("analyze_industry_chain_impact",
                  {"shock_percent": 15, "direction": "上升"},   # LLM 错误提交上升
                  question=QUESTION)
print("2. LLM提交上升 -> 引擎实际方向:", "下降" if "下降" in r2["scenario"] else "上升",
      "✔" if "下降" in r2["scenario"] else "✘")

r3 = execute_tool("analyze_supply_shock",
                  {"shock_percent": 25},                        # LLM 漏 sector + 错误幅度
                  question="钢铁供给收缩15%")
print("3. LLM漏sector+提交25% -> 引擎实际:", "钢铁+15.0%（覆盖成功）" if ("15.0%" in r3["scenario"] and "钢铁" in r3["scenario"] and "25%" not in r3["scenario"]) else f"✘ {r3['scenario'][:40]}")

r4 = execute_tool("analyze_industry_chain_impact",
                  {"shock_percent": 15},
                  question="房地产风险怎么看？")                 # 无幅度问题
print("4. 无幅度问题 -> blocked:", r4.get("blocked"), "✔" if r4.get("blocked") else "✘")
