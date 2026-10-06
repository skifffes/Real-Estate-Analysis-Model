# -*- coding: utf-8 -*-
"""验证 Ghosh 场景 LLM 路径不再 KeyError 降级"""
import json
import urllib.request

req = urllib.request.Request('http://localhost:8000/api/chat',
    data=json.dumps({'question': '钢铁减产10%对哪些行业影响最大'}).encode(),
    headers={'Content-Type': 'application/json'})
r = json.load(urllib.request.urlopen(req, timeout=180))
s = r.get('summary', '')
degraded = '已降级' in s
print('模型:', (r.get('impact') or {}).get('model', '')[:40])
print('摘要前80字:', s[:80])
print('工具轨迹:', [t['tool'] for t in r.get('tool_trace', [])][:4])
print('LLM路径', '正常（无降级标记）✔' if not degraded else '仍降级 ✘')
