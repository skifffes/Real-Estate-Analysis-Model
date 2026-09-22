"""Module 1: Agent 核心 —— LLM Function Calling 循环 + 规则引擎降级"""
import json
import re
import uuid

from ..config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from .tools import TOOL_SCHEMAS, execute_tool
from ..knowledge import rag
from ..models import input_output as io
from ..models import risk as risk_model

SYSTEM_PROMPT = """你是「房地产产业链风险分析智能体」，一名资深房地产金融风险分析师。

## 工作准则
1. 回答任何金融问题前，必须优先调用 search_knowledge_base 检索知识库获取依据。
2. 涉及"房地产投资/房价/销售 上升/下降 X%"等情景问题时，必须调用 analyze_industry_chain_impact 运行投入产出模型。
3. 对受影响最大的前几个行业调用 compute_risk_score 计算风险评分。
4. 涉及风险评估时调用 retrieve_similar_cases 做历史对比。
5. 若用户已上传数据（上下文中给出 file_id），调用 analyze_uploaded_data。

## 最终输出（必须是合法 JSON，不要输出其他任何文字）
{
  "summary": "分析摘要（150-300字，给出核心结论）",
  "risk_level": "低|关注|中|高|极高",
  "risk_score": 0-100,
  "affected_industries": [{"industry": "行业名", "impact_pct": 数值, "risk_score": 数值, "risk_level": "等级"}],
  "transmission_path": ["传导步骤1", "传导步骤2", ...],
  "model_basis": "模型依据（引用投入产出模型计算结果与乘数）",
  "data_basis": ["数据依据1（引用知识库来源）", ...],
  "key_indicators": ["建议关注指标1", ...]
}"""


class RiskAgent:
    def __init__(self):
        self.client = None
        if LLM_API_KEY:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
            except Exception:
                self.client = None

    @property
    def mode(self) -> str:
        return f"LLM ({LLM_MODEL})" if self.client else "规则引擎（未配置LLM_API_KEY，自动降级）"

    # ---------------- 主入口 ----------------
    def run(self, question: str, ctx: dict | None = None) -> tuple[dict, list]:
        """返回 (结构化报告, 工具调用轨迹)"""
        if self.client:
            try:
                return self._llm_run(question, ctx or {})
            except Exception as e:
                report, trace = self._rule_run(question, ctx or {})
                report["summary"] = f"[LLM调用失败已降级: {type(e).__name__}] " + report.get("summary", "")
                return report, trace
        return self._rule_run(question, ctx or {})

    # ---------------- LLM 路径 ----------------
    def _llm_run(self, question: str, ctx: dict) -> tuple[dict, list]:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ]
        if ctx.get("uploads"):
            files = "; ".join(f"{fid}({s.get('filename', '')})" for fid, s in ctx["uploads"].items())
            messages.append({"role": "user", "content": f"用户已上传数据文件，file_id 列表：{files}。如与问题相关请分析。"})

        trace = []
        for _ in range(8):  # 最多 8 轮工具调用
            resp = self.client.chat.completions.create(
                model=LLM_MODEL, messages=messages,
                tools=TOOL_SCHEMAS, tool_choice="auto", temperature=0.2,
            )
            msg = resp.choices[0].message
            if not msg.tool_calls:
                return self._parse_report(msg.content or ""), trace
            messages.append(msg)
            for tc in msg.tool_calls:
                args = json.loads(tc.function.arguments or "{}")
                result = execute_tool(tc.function.name, args, ctx)
                trace.append({"tool": tc.function.name, "args": args,
                              "result_preview": json.dumps(result, ensure_ascii=False)[:200]})
                messages.append({
                    "role": "tool", "tool_call_id": tc.id,
                    "content": json.dumps(result, ensure_ascii=False)[:6000],
                })
        return self._rule_run(question, ctx)  # 超轮次兜底

    @staticmethod
    def _parse_report(content: str) -> dict:
        m = re.search(r"\{[\s\S]*\}", content)
        if m:
            try:
                return json.loads(m.group(0))
            except json.JSONDecodeError:
                pass
        return {"summary": content, "risk_level": "中", "data_basis": []}

    # ---------------- 规则引擎路径（无 LLM 时的确定性分析流水线） ----------------
    def _rule_run(self, question: str, ctx: dict) -> tuple[dict, list]:
        trace = []
        q = question

        # 1. 知识库检索（必做）
        kb = rag.search(q, 3)
        trace.append({"tool": "search_knowledge_base", "args": {"query": q}, "result_preview": f"{len(kb)} 条命中"})

        # 2. 解析冲击情景
        pct, direction, has_shock = _parse_shock(q)

        impact = None
        if has_shock:
            impact = io.analyze_shock(pct, direction)
            trace.append({"tool": "analyze_industry_chain_impact",
                          "args": {"shock_percent": pct, "direction": direction},
                          "result_preview": f"总产出变动 {impact['total_output_change_yi']} 亿元"})

        # 3. 行业风险评分（受影响前5行业）
        industry_scores = []
        if impact:
            for row in impact["impact_matrix"][:5]:
                r = risk_model.industry_risk_from_impact(row["industry"], row["impact_pct"], row["debt_ratio"])
                industry_scores.append({"industry": row["industry"], "risk_score": r["risk_score"],
                                        "risk_level": r["risk_level"]})
                trace.append({"tool": "compute_risk_score", "args": {"industry": row["industry"]},
                              "result_preview": f"score={r['risk_score']} ({r['risk_level']})"})
        agg = risk_model.aggregate_risk(industry_scores)

        # 4. 历史案例
        similar = execute_tool("retrieve_similar_cases", {"event": q, "top_k": 2})
        trace.append({"tool": "retrieve_similar_cases", "args": {"event": q}, "result_preview": "2 条案例"})

        # 5. 上传数据（如有）
        upload_summary = None
        if ctx.get("uploads"):
            fid = next(iter(ctx["uploads"]))
            upload_summary = execute_tool("analyze_uploaded_data", {"file_id": fid}, ctx)
            trace.append({"tool": "analyze_uploaded_data", "args": {"file_id": fid}, "result_preview": "已分析"})

        return _compose_report(q, kb, impact, industry_scores, agg, similar.get("cases", []),
                               upload_summary), trace


# ---------------- 情景解析 ----------------
def _parse_shock(q: str) -> tuple[float, str, bool]:
    m = re.search(r"(上升|上涨|增长|下跌|下降|回落|下滑)\s*(\d+(?:\.\d+)?)\s*%?", q)
    if not m:
        return 0.0, "下降", False
    word, num = m.group(1), float(m.group(2))
    direction = "上升" if word in ("上升", "上涨", "增长") else "下降"
    return num, direction, True


# ---------------- 报告组装 ----------------
def _compose_report(question, kb, impact, industry_scores, agg, similar_cases, upload_summary) -> dict:
    kb_sources = [f"[{k['category']}] {k['source']}" for k in kb[:3]]
    if impact:
        top = impact["impact_matrix"][:5]
        top_desc = "、".join(f"{r['industry']}({r['impact_pct']:+.1f}%)" for r in top)
        summary = (
            f"针对「{question}」：基于14部门投入产出模型测算，情景「{impact['scenario']}」"
            f"将导致国民经济总产出变动约 {abs(impact['total_output_change_yi']):,.0f} 亿元"
            f"（占总产出 {abs(impact['total_output_change_pct'])}%）。"
            f"受影响最大的行业依次为：{top_desc}。"
            f"综合风险评分 {agg['risk_score']}（{agg['risk_level']}）。"
            f"传导路径为：房地产投资收缩 → 上游原材料需求下降 → 中游建造活动放缓 → 下游耐用品消费承压，"
            f"并通过金融渠道放大。"
        )
        model_basis = (f"列昂惕夫投入产出模型 X=(I-A)^(-1)Y：房地产乘数 {impact['real_estate_multiplier']}、"
                       f"建筑业乘数 {impact['construction_multiplier']}；冲击情景：{impact['scenario']}")
        transmission = [
            f"房地产最终需求{impact['scenario'].split('最终需求')[-1]}，直接冲击房地产与建筑业",
            "上游需求收缩：钢铁、建材、化工订单下降（生产成本渠道）",
            "中游放缓：机械设备、专业服务、建筑装饰活动减少",
            "下游承压：家电、家具等后周期消费需求下滑（收入-消费渠道）",
            "金融传导：房企信用风险暴露，银行敞口与抵押品价值承压（金融加速器渠道）",
        ]
        affected = [
            {"industry": r["industry"], "impact_pct": r["impact_pct"],
             "delta_output_yi": r["delta_output_yi"],
             "direct_effect_yi": r["direct_effect_yi"], "indirect_effect_yi": r["indirect_effect_yi"],
             **{"risk_score": next((s["risk_score"] for s in industry_scores if s["industry"] == r["industry"]),
                                    risk_model.industry_risk_from_impact(r["industry"], r["impact_pct"], r["debt_ratio"])["risk_score"])}}
            for r in top
        ]
    else:
        summary = f"针对「{question}」：已检索金融知识库，结合投入产出模型与风险评分框架给出定性分析。{agg['risk_level']}"
        model_basis = "基于投入产出模型与多指标风险评分框架（收入/债务/现金流/市场需求加权）"
        transmission = ["房地产销售/投资变动", "产业链上下游需求传导", "金融体系信用敞口变化"]
        affected = []
        # 无冲击情景时，若上传数据含风险评分则采用其结果
        if upload_summary and "risk_evaluation" in upload_summary:
            ev = upload_summary["risk_evaluation"]
            agg = {"risk_score": ev["risk_score"], "risk_level": ev["risk_level"]}
            summary = (f"针对「{question}」：基于上传数据「{upload_summary['filename']}」的风险指标"
                       f"（{upload_summary.get('shape', ['?'])[0]} 期数据），多指标加权模型测算综合风险评分 "
                       f"{ev['risk_score']}（{ev['risk_level']}）。各分项压力："
                       + "、".join(f"{k} {v}" for k, v in ev["components"].items()) + "。")

    if upload_summary:
        summary += f" 已结合上传数据「{upload_summary.get('filename', '')}」完成分析。"

    if similar_cases:
        case_names = "、".join(c["title"] for c in similar_cases)
        model_basis += f"。历史对标案例：{case_names}"

    return {
        "report_id": str(uuid.uuid4())[:8],
        "question": question,
        "summary": summary,
        "risk_level": agg["risk_level"],
        "risk_score": agg["risk_score"],
        "affected_industries": affected,
        "industry_scores": industry_scores,
        "transmission_path": transmission,
        "model_basis": model_basis,
        "data_basis": kb_sources + ([f"上传数据: {upload_summary['filename']}"] if upload_summary else []),
        "key_indicators": ["商品房销售面积同比", "房地产开发投资完成额同比", "新开工面积同比",
                           "70城房价指数环比", "房企现金短债比", "水泥/粗钢产量同比",
                           "家电与家具零售额同比", "银行房地产不良贷款率"],
        "similar_cases": [{"title": c["title"], "year": c["year"], "peak_impact": c["peak_impact"],
                           "lessons": c["lessons"]} for c in similar_cases],
        "impact": impact,
    }
