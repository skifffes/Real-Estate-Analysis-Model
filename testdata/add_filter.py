# -*- coding: utf-8 -*-
# cases.py 增加按原问题过滤的函数
add = """

def filter_by_question(cases: list[dict], question: str, min_score: float = 4.0) -> list[dict]:
    \"\"\"按用户原始问题做二次相关性校验（防 LLM 改写 event 参数塞入无关案例）。
    未通过阈值的案例直接过滤，返回空列表表示\"未检索到高度相关案例\"。\"\"\"
    if not cases or not question:
        return []
    kws = _keywords(question)
    out = []
    for c in cases:
        core = _keywords(c["trigger"] + "".join(c["transmission"]))
        text = _keywords(c["trigger"] + c["peak_impact"] + "".join(c["transmission"]) + c["title"])
        score = 2.0 * len(kws & core) + 1.0 * len(kws & text)
        if score >= min_score:
            out.append(c)
    return out
"""
p = r"d:\python\Financial\backend\app\knowledge\cases.py"
t = open(p, encoding="utf-8").read()
open(p, "w", encoding="utf-8").write(t + add)
print("cases.py: filter_by_question added")