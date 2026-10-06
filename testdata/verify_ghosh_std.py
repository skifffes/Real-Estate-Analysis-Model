# -*- coding: utf-8 -*-
"""验证地区适配版 Ghosh：API 端到端 + 与 Leontief 需求侧对照"""
import json
import urllib.request

def ask(q):
    req = urllib.request.Request('http://localhost:8000/api/chat',
        data=json.dumps({'question': q}).encode(),
        headers={'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(req, timeout=180))

r1 = ask('钢铁减产10%对哪些行业影响最大')
imp = r1.get('impact', {})
print('1. 钢铁减产10%（Ghosh-type 供给侧）')
print('   模型:', imp.get('model', '')[:55])
print('   合计:', imp.get('total_output_change_yi'), '亿元 |', imp.get('total_output_change_pct'), '%')
for row in (imp.get('impact_matrix') or [])[:4]:
    print(f"     {row['industry']}: {row['impact_pct']}% ({row['delta_output_yi']}亿)")
print('   供给乘数:', imp.get('supply_multiplier'))

r2 = ask('分析房地产投资下降15%的影响')
imp2 = r2.get('impact', {})
print('\n2. 房地产-15%（Leontief 需求侧，回归）')
print('   模型:', imp2.get('model', '')[:45])
print('   合计:', imp2.get('total_output_change_yi'), '亿元')

ok = (imp.get('model', '').startswith('Ghosh-type')
      and imp2.get('model', '').startswith('Leontief')
      and abs(imp.get('total_output_change_yi', 0)) < 100000)
print('\n', '全部通过 ✔' if ok else 'FAIL')
