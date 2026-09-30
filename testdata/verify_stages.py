# -*- coding: utf-8 -*-
"""验证传导三阶段输出"""
import json
import urllib.request

req = urllib.request.Request('http://localhost:8000/api/chat',
    data=json.dumps({'question': '分析房地产投资下降15%的影响'}).encode(),
    headers={'Content-Type': 'application/json'})
r = json.load(urllib.request.urlopen(req, timeout=180))
st = (r.get('impact') or {}).get('transmission_stages', {})
print('三阶段数量:', len(st.get('stages', [])))
for s in st.get('stages', []):
    print(f"  {s['name']} ({s['window']}) 压力={s['pressure']} 命中={s['hit_industries'][:3]}")
print('传导路径首行:', r['transmission_path'][0][:90] if r.get('transmission_path') else '无')
print('框架:', st.get('framework', '无')[:40])
