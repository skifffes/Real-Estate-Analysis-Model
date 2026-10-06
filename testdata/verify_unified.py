# -*- coding: utf-8 -*-
import json
import urllib.request

BASE = "http://localhost:8000"

def ask(q):
    req = urllib.request.Request(BASE + "/api/chat",
        data=json.dumps({"question": q}).encode(),
        headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=180))

def set_mode(mode):
    req = urllib.request.Request(BASE + "/api/agent/mode",
        data=json.dumps({"mode": mode}).encode(),
        headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=10)

results = {}
PV_Q = "光伏组件减产15%会有什么影响？"
RE_Q = "分析房地产投资下降15%的影响"

print("== PV (out-of-scope -> qualitative, no numbers) ==")
for mode in ["auto", "offline"]:
    set_mode(mode)
    r = ask(PV_Q)
    key = "pv_" + mode
    results[key] = {
        "no_score": r.get("risk_score") is None,
        "no_table": not r.get("affected_industries"),
        "no_cases": not r.get("similar_cases"),
    }
    print("  [%s]" % mode, results[key])

print("== RE (in-scope -> full numbers) ==")
for mode in ["auto", "offline"]:
    set_mode(mode)
    r = ask(RE_Q)
    key = "re_" + mode
    results[key] = {
        "table": len(r.get("affected_industries", [])) >= 3,
        "score": isinstance(r.get("risk_score"), (int, float)),
        "detail": len(r.get("industry_scores", [])) >= 3,
        "stages": len((r.get("impact") or {}).get("transmission_stages", {}).get("stages", [])) == 3,
    }
    print("  [%s]" % mode, results[key])

set_mode("offline")
r_off = ask(RE_Q)
n_cases = len(r_off.get("similar_cases", []))
print("\noffline cases count (fix check, should > 0):", n_cases)
set_mode("auto")

pv_ok = all(all(v.values()) for k, v in results.items() if k.startswith("pv"))
re_ok = all(all(v.values()) for k, v in results.items() if k.startswith("re"))
print("FINAL:", "ALL PASS" if pv_ok and re_ok and n_cases > 0 else "HAS FAIL")