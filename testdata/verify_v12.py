# -*- coding: utf-8 -*-
"""v1.2.0 三项功能验证：SQLite持久化 / 行业画像 / SSE流式"""
import json
import time
import urllib.request

BASE = 'http://localhost:8000'

print('== 1. SQLite 持久化 ==')
before = json.load(urllib.request.urlopen(BASE + '/api/reports', timeout=10))
n_before = len(before['items'])
print(f'  重启后恢复报告数: {n_before}（>0 即持久化生效）')
assert n_before > 0, 'SQLite 恢复失败'

print('== 2. 行业画像 ==')
p = json.load(urllib.request.urlopen(BASE + '/api/industry/' + urllib.parse.quote('建材'), timeout=10))
print(f"  {p['industry']}: 乘数={p['multiplier']} 负债率={p['debt_ratio']}% 上游{len(p['top_inputs'])}个 月度={list(p['latest_macro'].keys())}")
assert p['multiplier'] > 2 and p['top_inputs'], '画像数据异常'

print('== 3. SSE 流式 ==')
t0 = time.time()
n_events, final = 0, None
with urllib.request.urlopen(BASE + '/api/chat/stream?q=' + urllib.parse.quote('分析房地产投资下降10%的影响'), timeout=180) as resp:
    for raw in resp:
        line = raw.decode('utf-8').strip()
        if not line.startswith('data: ') or line == 'data: [DONE]':
            continue
        ev = json.loads(line[6:])
        if ev['type'] == 'tool':
            n_events += 1
            print(f"  [{time.time()-t0:5.1f}s] {'✓' if ev['status']=='done' else '→'} {ev['tool']}")
        elif ev['type'] == 'final':
            final = ev['report']
print(f"  工具事件 {n_events} 个，总耗时 {time.time()-t0:.1f}s，风险={final['risk_score']} {final['risk_level']}")
assert n_events >= 3 and final, 'SSE 异常'

# 4. 流式生成的报告也入库
after = json.load(urllib.request.urlopen(BASE + '/api/reports', timeout=10))
print(f'== 4. 报告入库 {n_before} -> {len(after['items'])} ==')
assert len(after['items']) == n_before + 1
print('\n全部通过 ✔')
