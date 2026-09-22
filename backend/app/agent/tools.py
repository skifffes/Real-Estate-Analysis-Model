"""Step 3: Agent Tool Schema（OpenAI Function Calling 格式）与工具执行分发"""
from ..knowledge import rag, cases as kb_cases
from ..models import input_output as io
from ..models import risk as risk_model

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": "检索房地产金融知识库（研究论文/投入产出模型资料/政策文件/历史风险案例）。回答任何金融问题前必须优先调用本工具获取依据。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "检索问题，如'房地产投资下降对上游产业链的影响'"},
                    "top_k": {"type": "integer", "description": "返回条数，默认4", "default": 4},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_industry_chain_impact",
            "description": "基于列昂惕夫投入产出模型 X=(I-A)^(-1)Y，测算房地产冲击对各行业产出的影响矩阵（直接效应+间接效应）。",
            "parameters": {
                "type": "object",
                "properties": {
                    "shock_percent": {"type": "number", "description": "冲击幅度百分比，正数，如15代表15%"},
                    "direction": {"type": "string", "enum": ["下降", "上升"], "description": "冲击方向"},
                },
                "required": ["shock_percent"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "compute_risk_score",
            "description": "多指标加权风险评分模型（0-100），输入行业收入变化、债务水平、现金流变化、市场需求变化。",
            "parameters": {
                "type": "object",
                "properties": {
                    "industry": {"type": "string", "description": "行业名称"},
                    "revenue_change": {"type": "number", "description": "收入同比变化%，如-10"},
                    "debt_ratio": {"type": "number", "description": "资产负债率%，如78"},
                    "cash_flow_change": {"type": "number", "description": "经营现金流变化%，如-20"},
                    "market_change": {"type": "number", "description": "市场需求变化%，如-12"},
                },
                "required": ["industry", "revenue_change", "debt_ratio", "cash_flow_change", "market_change"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "retrieve_similar_cases",
            "description": "检索历史房地产风险案例（日本1990/美国2008/恒大2021/海南1992），用于历史对比与经验参照。",
            "parameters": {
                "type": "object",
                "properties": {
                    "event": {"type": "string", "description": "风险事件描述"},
                    "top_k": {"type": "integer", "default": 2},
                },
                "required": ["event"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_uploaded_data",
            "description": "分析用户上传的数据文件（CSV/Excel），获取统计摘要与风险指标计算结果。",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_id": {"type": "string", "description": "上传文件ID"},
                },
                "required": ["file_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_dashboard_data",
            "description": "获取风险仪表盘数据：行业风险评分、产业链关系图、历史对比序列。",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]


def execute_tool(name: str, arguments: dict, ctx: dict | None = None) -> dict:
    """统一工具执行入口。ctx: {'uploads': {file_id: summary}}"""
    ctx = ctx or {}
    if name == "search_knowledge_base":
        return {"results": rag.search(arguments.get("query", ""), arguments.get("top_k", 4))}
    if name == "analyze_industry_chain_impact":
        return io.analyze_shock(
            float(arguments.get("shock_percent", 10)),
            arguments.get("direction", "下降"),
        )
    if name == "compute_risk_score":
        return risk_model.compute_risk_score(
            revenue_change=float(arguments.get("revenue_change", 0)),
            debt_ratio=float(arguments.get("debt_ratio", 50)),
            cash_flow_change=float(arguments.get("cash_flow_change", 0)),
            market_change=float(arguments.get("market_change", 0)),
        ) | {"industry": arguments.get("industry", "")}
    if name == "retrieve_similar_cases":
        return {"cases": kb_cases.retrieve_similar_cases(arguments.get("event", ""), arguments.get("top_k", 2))}
    if name == "analyze_uploaded_data":
        fid = arguments.get("file_id", "")
        summary = ctx.get("uploads", {}).get(fid)
        return summary or {"error": f"未找到文件 {fid}，请确认已上传"}
    if name == "get_dashboard_data":
        return ctx.get("dashboard", {})
    return {"error": f"未知工具: {name}"}
