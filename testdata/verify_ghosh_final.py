# -*- coding: utf-8 -*-
"""验证 Ghosh 口径统一后的四项反馈修正"""
import json
import urllib.request

def ask(q):
    req = urllib.request.Request('http://localhost:8000/api/chat',
        data=json.dumps({'question': q}).encode(),
        headers={'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(req, timeout=180))

# 1. Ghosh 数量冲击：公式与表述
r1 = ask('钢铁减产10%对哪些行业影响最大')
imp = r1.get('impact', {})
mb = r1.get('model_basis', '')
print('1. 钢铁减产10%:')
print('   model字段:', imp.get('model', '')[:50])
print('   model_basis含(I-B):', '(I-B)' in mb, '| 含"总产出系数化":', '总产出系数化' in mb)
print('   供给乘数:', imp.get('supply_multiplier'))
print('   摘要首60字:', r1.get('summary', '')[:60])

# 2. 价格类问题：不应进 Ghosh 数量模型
r2 = ask('水泥涨价10%会怎样')
no_ghosh = (r2.get('impact') or {}).get('model', '') == ''
print('2. 水泥涨价10%: 未触发Ghosh数量模型 =', no_ghosh, '| 摘要前60:', r2.get('summary', '')[:60])

# 3. Leontief 回归
r3 = ask('分析房地产投资下降15%的影响')
print('3. 房地产-15% Leontief 回归:', (r3.get('impact') or {}).get('model', '')[:45])
