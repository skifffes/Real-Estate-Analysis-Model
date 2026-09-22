"""Tool 3: 历史风险案例检索"""
import json
import re

from ..config import DATA_DIR

CASES = json.loads((DATA_DIR / "cases.json").read_text(encoding="utf-8"))


def _keywords(text: str) -> set:
    """中文 bigram + 英文单词"""
    kws = set()
    for run in re.findall(r"[\u4e00-\u9fa5]+", text):
        if len(run) == 1:
            kws.add(run)
        else:
            kws.update(run[i:i + 2] for i in range(len(run) - 1))
    kws.update(re.findall(r"[A-Za-z]{3,}", text))
    return kws


def retrieve_similar_cases(event: str, top_k: int = 2) -> list[dict]:
    """基于事件关键词（bigram）的案例相似度检索"""
    kws = _keywords(event)
    scored = []
    for c in CASES:
        text = c["trigger"] + c["peak_impact"] + "".join(c["transmission"]) + c["title"]
        # 触发因素与传导路径匹配权重更高
        core = _keywords(c["trigger"] + "".join(c["transmission"]))
        score = 2.0 * len(kws & core) + 1.0 * len(kws & _keywords(text))
        scored.append((score, c))
    scored.sort(key=lambda x: -x[0])
    return [c for s, c in scored[:top_k] if s > 0] or CASES[:top_k]
