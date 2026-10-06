# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"d:\python\Financial\backend")
from app.knowledge.cases import retrieve_similar_cases, filter_by_question

q = "分析房地产投资下降15%的影响"
res = retrieve_similar_cases(q, top_k=3)
print("retrieve:", len(res))
for c in res:
    print("  -", c["title"][:34])

filtered = filter_by_question(res, q)
print("filter:", len(filtered))
for c in filtered:
    print("  -", c["title"][:34])