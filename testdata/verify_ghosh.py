# -*- coding: utf-8 -*-
"""验证 Ghosh 供给侧工具自动路由"""
import json
import urllib.request

req = urllib.request.Request('http://localhost:8000/api/chat',
    data=json.dumps({'question': '钢铁减产10%对哪些行业影响最大'}).encode(),
    headers={'Content-Type': 'application/json'})
r = json.load(urllib.request.urlopen(req, timeout=180))
print('问题: 钢铁减产10%')
print('工具:', [t['tool'] for t in r.get('tool_trace', [])])
imp = r.get('impact', {})
print('模型:', imp.get('model', '无')[:60])
for row in (r.get('affected_industries') or [])[:4]:
    print(f"  {row['industry']}: {row['impact_pct']}%")
