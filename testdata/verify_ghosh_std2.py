# -*- coding: utf-8 -*-
"""验证标准 Ghosh (I-B)^(-1)：API 结果与独立重算对照"""
import json
import sys
import urllib.request

# 独立重算（另一个AI的方法）
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
