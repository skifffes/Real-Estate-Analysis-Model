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

cases = [
    ("分析房地产投资下降15%的影响", "quantified_leontief", "13部门", True, False),
    ("钢铁减产10%对哪些行业影响最大", "quantified_ghosh", "13部门", True, False),
    ("光伏组件减产15%会有什么影响？", "sector_unresolved", "无法映射至当前 13 部门", False, True),
    ("钢铁涨价10%会有什么影响", "price_qualitative", "不用于直接量化价格效应", False, True),
    ("房价下降10%会有什么影响", "asset_price_qualitative", "资产价格变化", False, True),
    ("钢铁减产有什么影响？", "missing_magnitude", "不会自行假设默认值", False, True),
]

all_ok = True
for q, exp_status, note_kw, expect_model, expect_note in cases:
    r = ask(q)
    status = r.get("analysis_status")
    reason = r.get("no_model_reason", "")
    md = download(r["report_id"])
    has_note_md = "模型适用性说明" in md
    ok = (status == exp_status
          and (note_kw in reason if expect_note else reason == "")
          and (has_note_md == expect_note))
    all_ok = all_ok and ok
    print(("OK " if ok else "FAIL"), q[:16], "-> status:", status, "| reason_kw:", (note_kw if expect_note else "none"), "| md_note:", has_note_md)

r = ask("Leontief模型是什么？")
status = r.get("analysis_status")
md = download(r["report_id"])
ok = status == "knowledge_only" and "模型适用性说明" not in md
all_ok = all_ok and ok
print(("OK " if ok else "FAIL"), "Leontief模型是什么？ -> status:", status, "| 无适用性说明:", "模型适用性说明" not in md)

print("FINAL:", "ALL PASS" if all_ok else "HAS FAIL")