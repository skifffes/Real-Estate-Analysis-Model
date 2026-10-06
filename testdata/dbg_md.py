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
print("has_model(impact):", r1.get("impact") is not None)
print("risk_score in report:", r1.get("risk_score"))
print()
print("== md1 headings ==")
for line in md1.splitlines():
    if line.startswith("#"):
        print(line)
print()
print("== md1 前600字 ==")
print(md1[:600])