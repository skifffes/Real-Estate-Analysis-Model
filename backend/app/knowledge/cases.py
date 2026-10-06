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


# 房地产领域词：案例库全部为房地产领域案例，问题含域词时给予领域相关性加成
_DOMAIN_KWS = ("房地产", "楼市", "房企", "住房", "地产", "商品房")


def _domain_bonus(text: str) -> float:
    return 3.0 if any(k in text for k in _DOMAIN_KWS) else 0.0


def retrieve_similar_cases(event: str, top_k: int = 2) -> list[dict]:
    """基于事件关键词（bigram）的案例相似度检索。
    评分 = 领域加成（问题属房地产领域 +3）+ 核心命中×2 + 文本命中×1；
    低于阈值返回空列表（不强行类比无关案例，如其他行业的供给冲击）。"""
    kws = _keywords(event)
    dom = _domain_bonus(event)
    scored = []
    for c in CASES:
        text = c["trigger"] + c["peak_impact"] + "".join(c["transmission"]) + c["title"]
        # 触发因素与传导路径匹配权重更高
        core = _keywords(c["trigger"] + "".join(c["transmission"]))
        score = dom + 2.0 * len(kws & core) + 1.0 * len(kws & _keywords(text))
        scored.append((score, c))
    scored.sort(key=lambda x: -x[0])
    return [c for s, c in scored[:top_k] if s >= 4.0][:top_k]


def filter_by_question(cases: list[dict], question: str, min_score: float = 4.0) -> list[dict]:
    """按用户原始问题做二次相关性校验（防 LLM 改写 event 参数塞入无关案例）。
    评分含房地产领域加成；未通过阈值的案例直接过滤。"""
    if not cases or not question:
        return []
    kws = _keywords(question)
    dom = _domain_bonus(question)
    out = []
    for c in cases:
        core = _keywords(c["trigger"] + "".join(c["transmission"]))
        text = _keywords(c["trigger"] + c["peak_impact"] + "".join(c["transmission"]) + c["title"])
        score = dom + 2.0 * len(kws & core) + 1.0 * len(kws & text)
        if score >= min_score:
            out.append(c)
    return out
