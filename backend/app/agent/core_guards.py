"""模型适用边界守卫（ROADMAP 可靠性设计·服务端硬校验）
数量模型（Leontief/Ghosh）仅允许数量型冲击问题调用；
价格/成本冲击与房价（资产价格）问题一律拦截——不信任 LLM 对提示词的遵守。
"""


def quantity_model_allowed(question: str) -> tuple[bool, str]:
    """校验数量模型调用是否被问题语义允许。返回 (allowed, reason)。"""
    if not question:
        return True, ""
    # 房价（资产价格）类 → 拦截
    house_kws = ("房价上涨", "房价下降", "房价下跌", "房价涨", "房价跌", "房价上升")
    if any(k in question for k in house_kws) and not any(
            k in question for k in ("投资", "新开工", "销售面积", "施工")):
        return False, "房价变化属资产价格变化，不直接等价于最终需求数量冲击，数量模型不适用"
    # 价格/成本类 → 拦截
    price_kws = ("涨价", "价格上升", "价格上涨", "成本上升", "原材料上涨")
    if any(k in question for k in price_kws):
        return False, "价格/成本冲击属价格效应，Ghosh 数量框架不适用，仅作定性机制分析"
    return True, ""
