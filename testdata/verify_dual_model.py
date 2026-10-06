# -*- coding: utf-8 -*-
"""双模型验证：供给侧(Ghosh) + 需求侧(Leontief) + 前端标注字段"""
import json
import urllib.request

def ask(q):
    req = urllib.request.Request('http://localhost:8000/api/chat',
        data=json.dumps({'question': q}).encode(),
        headers={'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(req, timeout=180))

# 1. Ghosh 供给侧
r1 = ask('钢铁减产10%对哪些行业影响最大')
m1 = (r1.get('impact') or {}).get('model', '')
print('1. 钢铁减产10% ->', m1[:45])
print('   工具:', [t['tool'] for t in r1.get('tool_trace', [])][:3])

# 2. Leontief 需求侧（回归确认未被破坏）
r2 = ask('分析房地产投资下降15%的影响')
m2 = (r2.get('impact') or {}).get('model', '')
print('2. 房地产投资下降15% ->', m2[:45])
print('   工具:', [t['tool'] for t in r2.get('tool_trace', [])][:3])

# 3. Dashboard 标注字段
d = json.load(urllib.request.urlopen('http://localhost:8000/api/dashboard', timeout=10))
print('3. Dashboard impact_model:', d.get('impact_model', '')[:50])

# 4. 报告 Markdown 标注
md = urllib.request.urlopen(f"http://localhost:8000/api/report/{r2['report_id']}/download", timeout=10).read().decode('utf-8')
tag = '本次分析采用' in md
print('4. 报告MD模型标注:', 'OK' if tag else 'FAIL')

ok = m1.startswith('Ghosh') and m2.startswith('Leontief')
print('\n', '全部通过 ✔' if ok else '存在FAIL')
