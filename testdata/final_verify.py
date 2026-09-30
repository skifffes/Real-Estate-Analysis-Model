# -*- coding: utf-8 -*-
"""最终验证：月度数据接入 + 新文档入库 + 真实负债率 + 报告链路"""
import json
import urllib.request

BASE = 'http://localhost:8000'

# 1. Dashboard 月度数据
d = json.load(urllib.request.urlopen(BASE + '/api/dashboard', timeout=10))
s = d.get('transmission_monthly', {}).get('series', {})
print('1. 月度序列:', list(s.keys()))
nk = s.get('新开工同比', {})
print('   新开工最新3期:', dict(list(nk.items())[-3:]))

# 2. 真实负债率（通过上传样本验证风险评分口径变化）
req = urllib.request.Request(BASE + '/api/chat',
    data=json.dumps({'question': '分析房地产投资下降15%的影响'}).encode(),
    headers={'Content-Type': 'application/json'})
r = json.load(urllib.request.urlopen(req, timeout=180))
print('2. chat 风险:', r['risk_score'], r['risk_level'], '| 工具:', len(r.get('tool_trace', [])))

# 3. 新文档知识库检索
for q in ['销售的回暖何时传导到新开工', '中国房地产下行对宏观经济影响']:
    res = json.load(urllib.request.urlopen(
        BASE + '/api/kb/search?q=' + urllib.parse.quote(q), timeout=30))
    tops = [x['source'][:45] for x in res['results'][:2]]
    print(f'3. 检索[{q[:14]}] ->', tops)

# 4. 报告下载无 undefined
md = urllib.request.urlopen(f"{BASE}/api/report/{r['report_id']}/download", timeout=10).read().decode('utf-8')
print('4. 报告:', len(md), '字符 | undefined:', 'undefined' in md)
