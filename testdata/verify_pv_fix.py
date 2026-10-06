# -*- coding: utf-8 -*-
import json
import urllib.request

def ask(q):
    req = urllib.request.Request("http://localhost:8000/api/chat",
        data=json.dumps({"question": q}).encode(),
        headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=180))

r = ask("光伏组件减产15%会有什么影响？")
md = {
    "no_score": r.get("risk_score") is None,
    "no_table": not r.get("affected_industries"),
    "no_scores": not r.get("industry_scores"),
    "no_cases": not r.get("similar_cases"),
    "state_note": "模型状态" in r.get("summary", ""),
}
for k, v in md.items():
    print("OK" if v else "FAIL", k)

r2 = ask("分析房地产投资下降15%的影响")
ok2 = {
    "table": len(r2.get("affected_industries", [])) > 0,
    "score": isinstance(r2.get("risk_score"), (int, float)),
    "cases": len(r2.get("similar_cases", [])) > 0,
    "stages": len((r2.get("impact") or {}).get("transmission_stages", {}).get("stages", [])) == 3,
}
for k, v in ok2.items():
    print("OK" if v else "FAIL", "regress", k)
print("ALL", "PASS" if all(md.values()) and all(ok2.values()) else "HAS-FAIL")