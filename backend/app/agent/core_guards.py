"""模型适用边界守卫（服务端硬校验，架构级模型路由保证）

完整路由守卫：不仅拦截价格/房价问题，还校验 LLM 选择的模型是否与问题类型匹配：
  - 数量型需求冲击（房地产投资/销售…）→ 仅允许 Leontief
  - 数量型供给冲击（钢铁减产/供给收缩…）→ 仅允许 Ghosh
  - 价格/成本、房价（资产价格）问题 → 禁止一切数量模型
不信任 LLM 对提示词的遵守，服务端最终裁决。
"""


def _has_house_price(q: str) -> bool:
    return any(k in q for k in ("房价上涨", "房价下降", "房价下跌", "房价涨", "房价跌", "房价上升"))


def _has_price(q: str) -> bool:
    return any(k in q for k in ("涨价", "价格上升", "价格上涨", "成本上升", "原材料上涨"))


def _has_supply(q: str) -> bool:
    return any(k in q for k in ("减产", "供给收缩", "供给下降", "停产", "限产", "供给减少"))


def expected_model(question: str) -> str:
    """按问题语义判定应使用的模型：'leontief' / 'ghosh' / 'qualitative'"""
    if not question:
        return "qualitative"
    if _has_house_price(question) and not any(
            k in question for k in ("投资", "新开工", "销售面积", "施工")):
        return "qualitative"           # 房价 = 资产价格变化 → 定性
    if _has_price(question):
        return "qualitative"           # 价格/成本冲击 → 定性
    if _has_supply(question):
        return "ghosh"                 # 数量型供给冲击
    return "leontief"                  # 默认：数量型需求冲击


def quantity_model_allowed(question: str) -> tuple[bool, str]:
    """旧接口兼容：数量模型（Leontief/Ghosh）是否被允许"""
    em = expected_model(question)
    if em == "qualitative":
        return False, _qualitative_reason(question)
    return True, ""


def check_tool_allowed(tool: str, question: str) -> tuple[bool, str]:
    """完整路由守卫：校验 LLM 选择的模型是否与问题语义匹配。返回 (allowed, reason)。"""
    em = expected_model(question)
    if em == "qualitative":
        if tool in ("analyze_industry_chain_impact", "analyze_supply_shock"):
            return False, _qualitative_reason(question)
        return True, ""
    if em == "ghosh" and tool == "analyze_industry_chain_impact":
        return False, "本问题属数量型供给冲击，应使用 Ghosh 供给侧模型（analyze_supply_shock），不适用 Leontief 需求侧模型"
    if em == "leontief" and tool == "analyze_supply_shock":
        return False, "本问题属数量型需求冲击，应使用 Leontief 需求侧模型（analyze_industry_chain_impact），不适用 Ghosh 供给侧模型"
    return True, ""


def _qualitative_reason(question: str) -> str:
    if _has_house_price(question):
        return "房价变化属资产价格变化，不直接等价于最终需求数量冲击，数量模型不适用"
    return "价格/成本冲击属价格效应，Ghosh/Leontief 数量框架不适用，仅作定性机制分析"
