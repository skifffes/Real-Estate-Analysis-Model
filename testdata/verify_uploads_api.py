# -*- coding: utf-8 -*-
"""验证上传文件查看接口（列表/详情/原文）"""
import json
import urllib.request
import uuid

BASE = 'http://localhost:8000'

# 触发一次上传（服务重启后内存清空）
body = open(r'd:/python/Financial/testdata/样本_房地产行业风险指标.csv', 'rb').read()
b = '----' + uuid.uuid4().hex
head = (f'--{b}\r\nContent-Disposition: form-data; name="file"; filename="risk.csv"\r\n'
        f'Content-Type: text/csv\r\n\r\n').encode()
req = urllib.request.Request(BASE + '/api/upload',
                             data=head + body + f'\r\n--{b}--\r\n'.encode(),
                             headers={'Content-Type': f'multipart/form-data; boundary={b}'})
u = json.load(urllib.request.urlopen(req, timeout=30))
fid = u['file_id']
print('上传成功:', u['filename'], u['shape'])

# 1. 列表
lst = json.load(urllib.request.urlopen(BASE + '/api/uploads', timeout=10))
print(f"1. GET /api/uploads -> {len(lst['items'])} 个文件 | 首个: {lst['items'][0]['filename']} 评分={lst['items'][0]['risk_score']}")

# 2. 详情
one = json.load(urllib.request.urlopen(f'{BASE}/api/upload/{fid}', timeout=10))
print(f"2. GET /api/upload/{fid} -> {one['filename']} {one['shape']} 识别指标={list((one.get('risk_evaluation') or {}).get('detected_indicators', {}).values())}")

# 3. 原文
raw = urllib.request.urlopen(f'{BASE}/api/upload/{fid}/raw', timeout=10).read().decode('utf-8')
print(f"3. GET /api/upload/{fid}/raw -> {len(raw)} 字符，首行: {raw.splitlines()[0]}")
