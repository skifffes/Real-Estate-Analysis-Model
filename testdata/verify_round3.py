# -*- coding: utf-8 -*-
"""验证第三轮3项残留清理 + 最终一致性"""
import json
import urllib.request

def ask(q):
    req = urllib.request.Request('http://localhost:8000/api/chat',
        data=json.dumps({'question': q}).encode(),
        headers={'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(req, timeout=180))

# 1. Ghosh 报告摘要：无"成本推动型"
r1 = ask('钢铁减产10%对哪些行业影响最大')
s1 = r1.get('summary', '')
print('1. Ghosh摘要: 含"供给约束型"=', '供给约束型' in s1, '| 含旧"成本推动型"=', '本情景属于成本推动型' in s1)

# 2. 传导路径
t1 = '|'.join(r1.get('transmission_path', []))
print('   传导路径: 成本上升作为结果保留=', '成本上升' in t1)

# 2b. 三阶段名称（供给侧框架）
st1 = (r1.get('impact') or {}).get('transmission_stages', {}).get('stages', [])
print('   三阶段:', [(s['name'], s['pressure']) for s in st1])

# 3. Leontief 回归
r2 = ask('分析房地产投资下降15%的影响')
st2 = (r2.get('impact') or {}).get('transmission_stages', {})
print('3. Leontief 三阶段:', [(s['name'], s['pressure']) for s in st2.get('stages', [])])

# 4. 报告MD下载验证标题动态化
md = urllib.request.urlopen(f"http://localhost:8000/api/report/{r2['report_id']}/download", timeout=10).read().decode('utf-8')
print('4. Leontief报告MD标题: 六案例=', '六案例归纳框架' in md, '| 无供给约束误挂=', '供给约束传导框架' not in md)
