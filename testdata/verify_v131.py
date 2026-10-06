# -*- coding: utf-8 -*-
"""v1.3.1 验证：外部评审5项修正"""
import json
import urllib.request

def ask(q):
    req = urllib.request.Request('http://localhost:8000/api/chat',
        data=json.dumps({'question': q}).encode(),
        headers={'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(req, timeout=180))

# 1. 供给侧三阶段串台（Ghosh 报告不应出现六房企案例规律）
r1 = ask('钢铁减产10%对哪些行业影响最大')
st1 = (r1.get('impact') or {}).get('transmission_stages', {})
t1 = json.dumps(st1, ensure_ascii=False)
print('1. Ghosh三阶段串台: framework含"供给约束"=', '供给约束' in t1,
      '| 无六房企串台=', '恒大' not in t1 and '碧桂园' not in t1)

# 2. 14→13部门
s = r1.get('summary', '')
print('2. 摘要含13部门:', '13部门' in s, '| 无14部门残留:', '14部门' not in s)

# 3. 房价拦截
r3 = ask('房价下降10%会有什么影响')
no_model3 = (r3.get('impact') or {}).get('model', '') == ''
print('3. 房价-10%: 未进数量模型 =', no_model3, '| 摘要含资产价格定性:', '资产价格' in r3.get('summary', ''))

# 4. Leontief 回归 + 口径措辞
r4 = ask('分析房地产投资下降15%的影响')
s4 = r4.get('summary', '')
print('4. Leontief回归: 摘要含"产业关联压力"=', '产业关联压力' in s4,
      '| 含情景措辞=', '情景测算' in s4,
      '| 无"国民经济总产出"强表述=', '国民经济总产出' not in s4)

# 5. 行业评分明细由引擎生成
scores4 = r4.get('industry_scores', [])
print('5. 行业评分明细由引擎生成:', len(scores4), '个')
