# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"d:\python\Financial\backend")
from app.knowledge.cases import _keywords, CASES

q = "光伏组件减产15%会有什么影响？"
kws = _keywords(q)
print("query bigrams:", sorted(kws))
for c in CASES:
    core = _keywords(c["trigger"] + "".join(c["transmission"]))
    text = _keywords(c["trigger"] + c["peak_impact"] + "".join(c["transmission"]) + c["title"])
    score = 2.0 * len(kws & core) + 1.0 * len(kws & text)
    if score >= 3:
        print(f"{c['title'][:30]}: score={score:.1f} core_hits={sorted(kws & core)[:6]}")