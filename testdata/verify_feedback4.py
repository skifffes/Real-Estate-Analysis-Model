# -*- coding: utf-8 -*-
"""验证反馈4项修正：docstring/价格分支/工具描述/口径统一"""
import json
import urllib.request

def ask(q):
    req = urllib.request.Request('http://localhost:8000/api/chat',
        data=json.dumps({'question': q}).encode(),
        headers={'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(req, timeout=180))

# 1. 价格分支（bug修复验证）：不再误入Leontief
r = ask('钢铁涨价10%有什么影响')
no_leontief = (r.get('impact') or {}).get('model', '') == ''
print('1. 钢铁涨价10%: 未进Leontief/Ghosh =', no_leontief)
print('   工具:', [t['tool'] for t in r.get('tool_trace', [])][:3])
print('   摘要:', r.get('summary', '')[:90])

# 2. Ghosh 数量冲击表述
r2 = ask('钢铁减产10%对哪些行业影响最大')
mb = r2.get('model_basis', '')
print('2. 钢铁减产10%: model_basis含(I-B)=', '(I-B)' in mb, '| 含"总产出系数化"=', '总产出系数化' in mb, '| 含"暴露强度"=', '暴露强度' in mb)
print('   摘要含情景测算措辞:', '情景测算' in r2.get('summary', ''))

# 3. Leontief 回归
r3 = ask('分析房地产投资下降15%的影响')
print('3. 房地产-15%:', (r3.get('impact') or {}).get('model', '')[:40])
