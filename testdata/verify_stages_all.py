# -*- coding: utf-8 -*-
"""验证三阶段在 首页/Dashboard/报告中心 三处均有体现"""
import json
import urllib.request

req = urllib.request.Request('http://localhost:8000/api/chat',
    data=json.dumps({'question': '分析房地产投资下降15%的影响'}).encode(),
    headers={'Content-Type': 'application/json'})
r = json.load(urllib.request.urlopen(req, timeout=180))
rid = r['report_id']

# 1. 首页报告（chat 响应）
ok1 = len((r.get('impact') or {}).get('transmission_stages', {}).get('stages', [])) == 3
print('1. 首页报告卡三阶段:', 'OK' if ok1 else 'FAIL')

# 2. Dashboard
d = json.load(urllib.request.urlopen('http://localhost:8000/api/dashboard', timeout=10))
st = d.get('transmission_stages', {})
ok2 = len(st.get('stages', [])) == 3
print('2. Dashboard三阶段:', 'OK' if ok2 else 'FAIL',
      '| 压力:', [s['pressure'] for s in st.get('stages', [])])

# 3. 报告中心 Markdown（后端生成+下载）
md = urllib.request.urlopen(f'http://localhost:8000/api/report/{rid}/download', timeout=10).read().decode('utf-8')
ok3 = ('传导三阶段预判' in md and '直接冲击期' in md and '跨案例规律' in md)
print('3. 报告Markdown三阶段:', 'OK' if ok3 else 'FAIL')
seg = md[md.find('### 传导三阶段预判'):md.find('### 传导三阶段预判') + 300]
print('   预览:', seg.replace('\n', ' | ')[:200])
print('\n全部', '通过 ✔' if (ok1 and ok2 and ok3) else '未通过')
