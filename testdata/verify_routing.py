# -*- coding: utf-8 -*-
"""外部评审第四轮验证：路由修复 + 工具校验 + 复合情景标注"""
import json
import urllib.request

def ask(q):
    req = urllib.request.Request('http://localhost:8000/api/chat',
        data=json.dumps({'question': q}).encode(),
        headers={'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(req, timeout=180))

def model_of(r):
    return (r.get('impact') or {}).get('model', '')

# 反馈列的 7 个场景
cases = [
    ('房地产投资下降15%', 'Leontief'),          # 应进 Leontief（修复核心）
    ('房地产销售面积下降10%', 'Leontief'),       # 应进 Leontief
    ('钢铁减产10%', 'Ghosh'),                   # 应进 Ghosh（修复核心）
    ('钢铁供给收缩10%', 'Ghosh'),               # 应进 Ghosh
    ('房价下降10%', ''),                        # 应定性（无模型）
    ('钢铁涨价10%', ''),                        # 应定性（无模型）
    ('钢铁价格上涨10%', ''),                    # 应定性（反馈特别点名的场景）
]
all_ok = True
for q, expect in cases:
    r = ask(q)
    m = model_of(r)
    got = 'Leontief' if m.startswith('Leontief') else ('Ghosh' if m.startswith('Ghosh') else '')
    ok = got == expect
    all_ok = all_ok and ok
    print(f"{'OK' if ok else 'FAIL'} {q} -> {got or '定性'}（期望 {expect or '定性'}）")

# 复合情景标注
r = ask('房地产投资下降15%')
sc = (r.get('impact') or {}).get('scenario', '')
print(f"\n复合情景标注: {'OK' if '复合压力测试' in sc else 'FAIL'} -> {sc[:60]}")
print('\n路由修复', '全部通过' if all_ok else '存在FAIL')
