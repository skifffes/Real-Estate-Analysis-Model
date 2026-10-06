# -*- coding: utf-8 -*-
import json
import urllib.request

def ask(q):
    req = urllib.request.Request("http://localhost:8000/api/chat",
        data=json.dumps({"question": q}).encode(),
        headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=180))

def download(rid):
    return urllib.request.urlopen("http://localhost:8000/api/report/" + rid + "/download", timeout=10).read().decode("utf-8")

r1 = ask("光伏组件减产15%会有什么影响？")
md1 = download(r1["report_id"])
c1 = {
    "no_RA": "## 2. Risk Assessment" not in md1,
    "no_AI": "## 4. Affected Industries" not in md1,
    "has_note": "模型适用性说明" in md1,
    "note_text": "未通过当前 13 部门模型口径校验" in md1,
    "no_dash": "综合风险评分：—" not in md1,
}
for k, v in c1.items():
    print("OK" if v else "FAIL", k)

r2 = ask("分析房地产投资下降15%的影响")
md2 = download(r2["report_id"])
seg = md2.split("## 2.")[1].split("## 3.")[0] if "## 2." in md2 else ""
c2 = {
    "RA_chapter": "## 2. Risk Assessment" in md2,
    "AI_chapter": "## 4. Affected Industries" in md2,
    "score": "综合风险评分" in seg,
    "no_dash": "—" not in seg,
}
for k, v in c2.items():
    print("OK" if v else "FAIL", "regress", k)
print("FINAL:", "ALL PASS" if all(c1.values()) and all(c2.values()) else "HAS FAIL")