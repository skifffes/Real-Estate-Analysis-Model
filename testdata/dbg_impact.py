# -*- coding: utf-8 -*-
import json
import urllib.request

req = urllib.request.Request("http://localhost:8000/api/chat",
    data=json.dumps({"question": "光伏组件减产15%会有什么影响？"}).encode(),
    headers={"Content-Type": "application/json"})
r = json.load(urllib.request.urlopen(req, timeout=180))
imp = r.get("impact")
print("impact is None:", imp is None)
print("impact type:", type(imp).__name__)
if isinstance(imp, dict):
    print("impact keys:", list(imp.keys())[:6])
print("risk_score:", r.get("risk_score"))
print("affected_industries:", r.get("affected_industries"))
print("summary tail:", r.get("summary", "")[-90:])