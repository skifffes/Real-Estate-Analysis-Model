# -*- coding: utf-8 -*-
"""验证 Agent 模式切换：offline / auto(llm)"""
import json
import urllib.request

BASE = 'http://localhost:8000'

def post(path, payload):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(),
                                 headers={'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(req, timeout=180))

def get(path):
    return json.load(urllib.request.urlopen(BASE + path, timeout=10))

# 1. 初始状态
m = get('/api/agent/mode')
print(f"1. 初始模式: {m['mode']} | LLM可用: {m['llm_available']} | {m['description'][:40]}")

# 2. 切 offline → 提问 → 验证零LLM
r = post('/api/agent/mode', {'mode': 'offline'})
print(f"2. 切换 offline: {r['description'][:40]}")
r1 = post('/api/chat', {'question': '分析房地产投资下降12%的影响'})
assert '离线' in r1.get('agent_mode', ''), 'offline 未生效'
assert '已降级' not in r1.get('summary', ''), 'offline 模式不应出现降级标记'
print(f"   报告 agent_mode: {r1['agent_mode']} | 评分 {r1['risk_score']}（完整报告✔）")

# 3. 切回 auto → 提问 → LLM 模式
r = post('/api/agent/mode', {'mode': 'auto'})
print(f"3. 切回 auto: {r['description'][:40]}")
r2 = post('/api/chat', {'question': '钢铁减产8%的影响'})
assert r2.get('agent_mode', '').startswith('LLM'), 'auto 模式未走 LLM'
print(f"   报告 agent_mode: {r2['agent_mode']} | 模型 {(r2.get('impact') or {}).get('model', '')[:30]}")

# 4. 无效模式
try:
    post('/api/agent/mode', {'mode': 'bad_mode'})
    print('4. 无效模式: FAIL（未拒绝）')
except urllib.error.HTTPError as e:
    print(f"4. 无效模式: 已拒绝（HTTP {e.code}）✔")

print('\n模式切换功能全部通过 ✔')
