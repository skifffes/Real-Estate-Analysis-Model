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


import re


def has_explicit_shock(question: str) -> bool:
    """是否存在明确的数量冲击幅度（如'下降15%'、'减产10%'）。
    模型运行的前提条件：没有明确幅度的问题不进入数量模型（防 LLM 脑补默认值）。"""
    return bool(re.search(
        r"(上升|上涨|增长|下跌|下降|回落|下滑|减产|收缩|供给收缩|供给下降)\s*\d+(\.\d+)?\s*%?",
        question))


def expected_model(question: str) -> str:
    """按问题语义判定应使用的模型：'leontief' / 'ghosh' / 'qualitative' / 'none'
    'qualitative' = 价格/成本冲击或房价（资产价格）变化 → 定性机制分析；
    'none' = 无明确量化冲击幅度，或行业无法映射到模型 13 部门口径 → 数量模型全部禁止。
    注意：价格/房价判断优先于幅度检查（带幅度的价格冲击仍属定性范畴）。"""
    if not question:
        return "none"
    if _has_house_price(question) and not any(
            k in question for k in ("投资", "新开工", "销售面积", "施工")):
        return "qualitative"           # 房价 = 资产价格变化 → 定性
    if _has_price(question):
        return "qualitative"           # 价格/成本冲击 → 定性（即使带幅度）
    if _has_supply(question):
        # 数量型供给冲击：还须行业能映射到模型 13 部门口径（不猜测行业）
        from app.agent.core import _supply_sector
        if not _supply_sector(question):
            return "none"
        return "ghosh"                 # 数量型供给冲击
    if not has_explicit_shock(question):
        return "none"                  # 无明确冲击幅度 → 数量模型全部禁止
    return "leontief"                  # 数量型需求冲击


def quantity_model_allowed(question: str) -> tuple[bool, str]:
    """旧接口兼容：数量模型（Leontief/Ghosh）是否被允许"""
    em = expected_model(question)
    if em == "qualitative":
        return False, _qualitative_reason(question)
    return True, ""


def check_tool_allowed(tool: str, question: str) -> tuple[bool, str]:
    """完整路由守卫：校验模型调用是否满足适用条件。返回 (allowed, reason)。
    四层检查：明确冲击幅度 → 问题类型 → 模型匹配。"""
    em = expected_model(question)
    if em == "none":
        if tool in ("analyze_industry_chain_impact", "analyze_supply_shock"):
            return False, "问题未提供明确的量化冲击幅度（如'下降15%'），数量模型不适用；纯知识/定性问题不应触发数量测算"
        return True, ""
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
    if not has_explicit_shock(question):
        return "问题未提供明确的量化冲击幅度，数量模型不适用"
    return "价格/成本冲击属价格效应，Ghosh/Leontief 数量框架不适用，仅作定性机制分析"
