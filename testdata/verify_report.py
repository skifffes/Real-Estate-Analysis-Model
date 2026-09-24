# -*- coding: utf-8 -*-
"""验证报告生成无 undefined + 定性描述"""
import json
import urllib.request

req = urllib.request.Request('http://localhost:8000/api/chat',
    data=json.dumps({'question': '分析房地产投资下降12%的影响'}).encode(),
    headers={'Content-Type': 'application/json'})
r = json.load(urllib.request.urlopen(req, timeout=180))
rid = r['report_id']
md = urllib.request.urlopen(f'http://localhost:8000/api/report/{rid}/download', timeout=10).read().decode('utf-8')
print('报告长度:', len(md))
print('undefined 残留:', 'undefined' in md)
print('含冲击程度列:', '冲击程度' in md)
rows = [l for l in md.splitlines() if l.startswith('| 房地产') or l.startswith('| 建筑业')]
print('矩阵行示例:')
for row in rows[:2]:
    print(' ', row)
