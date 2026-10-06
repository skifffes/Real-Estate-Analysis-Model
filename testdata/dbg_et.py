# -*- coding: utf-8 -*-
# 直接复现 execute_tool 的案例分支
import sys
sys.path.insert(0, r"d:\python\Financial\backend")
from app.agent.tools import execute_tool

q = "分析房地产投资下降15%的影响"
r = execute_tool("retrieve_similar_cases", {"event": q, "top_k": 3}, question=q)
print("cases:", len(r.get("cases", [])))
print("note:", r.get("note", "none"))
for c in r.get("cases", []):
    print("  -", c["title"][:34])