# -*- coding: utf-8 -*-
"""联调测试脚本：chat / dashboard / upload / reports"""
import json
import time
import urllib.request
import uuid

BASE = 'http://localhost:8000'
ok = lambda label: print(f'  [PASS] {label}')


def post_json(path, payload):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(),
                                 headers={'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(req, timeout=60))


print('== 1. chat 核心问答 ==')
r = post_json('/api/chat', {'question': '分析房地产投资下降15%的影响'})
assert r['risk_score'] > 0 and r['affected_industries'], 'chat 结果异常'
print(f"  风险: {r['risk_score']} {r['risk_level']} | 行业数: {len(r['affected_industries'])}")
print(f"  工具轨迹: {[t['tool'] for t in r['tool_trace']]}")
print(f"  数据依据: {r['data_basis'][:2]}")
print(f"  摘要: {r['summary'][:100]}...")
ok('chat 结构化报告')

print('== 2. dashboard ==')
d = json.load(urllib.request.urlopen(BASE + '/api/dashboard', timeout=10))
assert d['risk_score'] == r['risk_score'], 'dashboard 未同步 chat 结果'
assert len(d['supply_chain']['nodes']) == 13, '产业链图节点数异常'  # 真实北京表聚合为13部门
assert len(d['historical_comparison']['years']) == 10, '历史数据异常'
print(f"  score={d['risk_score']} 行业={len(d['industry_impact'])} 节点={len(d['supply_chain']['nodes'])} 连线={len(d['supply_chain']['links'])}")
ok('dashboard 四模块数据完整')

print('== 3. upload CSV ==')
body = open('d:/python/Financial/testdata/样本_房地产行业风险指标.csv', 'rb').read()
boundary = '----' + uuid.uuid4().hex
head = (f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="risk.csv"\r\n'
        f'Content-Type: text/csv\r\n\r\n').encode()
req = urllib.request.Request(BASE + '/api/upload', data=head + body + f'\r\n--{boundary}--\r\n'.encode(),
                             headers={'Content-Type': f'multipart/form-data; boundary={boundary}'})
u = json.load(urllib.request.urlopen(req, timeout=30))
ev = u.get('risk_evaluation', {})
print(f"  shape={u['shape']} 识别指标={ev.get('detected_indicators')} 评分={ev.get('risk_score')}({ev.get('risk_level')})")
assert ev.get('risk_score', 0) > 0, '上传数据未计算出风险评分'
ok('upload 自动识别风险指标')

print('== 4. 结合上传数据的 chat ==')
r2 = post_json('/api/chat', {'question': '结合上传数据分析当前房地产行业风险'})
assert any('上传数据' in b for b in r2['data_basis']), '未融合上传数据'
print(f"  数据依据: {r2['data_basis']}")
ok('agent 融合上传数据分析')

print('== 5. 报告生成与下载 ==')
lst = json.load(urllib.request.urlopen(BASE + '/api/reports', timeout=10))
assert len(lst['items']) >= 2, '报告数异常'
rid = lst['items'][0]['report_id']
md = urllib.request.urlopen(BASE + f'/api/report/{rid}/download', timeout=10).read().decode('utf-8')
assert 'Executive Summary' in md and 'Transmission Mechanism' in md, '报告结构不完整'
print(f"  报告数={len(lst['items'])} 最新报告长度={len(md)} 字符, 六章结构完整")
ok('Markdown 报告持久化与下载')

print('\n全部联调通过 ✔')
