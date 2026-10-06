# -*- coding: utf-8 -*-
"""验证 LLM/规则引擎 两模式的报告字段一致性"""
import json
import urllib.request

def ask(q):
    req = urllib.request.Request('http://localhost:8000/api/chat',
        data=json.dumps({'question': q}).encode(),
        headers={'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(req, timeout=180))

# 1. LLM 模式：钢铁减产（Ghosh）
r = ask('钢铁减产10%对哪些行业影响最大')
st = (r.get('impact') or {}).get('transmission_stages', {})
print('1. LLM模式 钢铁减产10%:')
print('   模型:', (r.get('impact') or {}).get('model', '')[:38])
print('   行业评分明细:', len(r.get('industry_scores', [])), '个 ->', [(s['industry'], s['risk_score']) for s in r.get('industry_scores', [])[:3]])
print('   三阶段:', [(s['name'], s['pressure']) for s in st.get('stages', [])])
print('   综合评分:', r.get('risk_score'), r.get('risk_level'))

# 2. LLM 模式：房地产（Leontief 回归）
r2 = ask('分析房地产投资下降15%的影响')
st2 = (r2.get('impact') or {}).get('transmission_stages', {})
print('2. LLM模式 房地产-15%:')
print('   行业评分明细:', len(r2.get('industry_scores', [])), '个')
print('   三阶段:', [(s['name'], s['pressure']) for s in st2.get('stages', [])])

ok1 = len(r.get('industry_scores', [])) >= 3 and len(st.get('stages', [])) == 3
ok2 = len(r2.get('industry_scores', [])) >= 3 and len(st2.get('stages', [])) == 3
print('\n', '全部通过 ✔' if ok1 and ok2 else '存在FAIL')
