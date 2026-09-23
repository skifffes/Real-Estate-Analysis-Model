"""Module 5: 报告生成 —— 结构化 JSON → Markdown 金融分析报告"""
from ..config import REPORTS_DIR


def _fmt(v, fmt_str="{:+,.0f}"):
    return fmt_str.format(v) if isinstance(v, (int, float)) else "-"


def _industries_md(rows: list[dict]) -> str:
    if not rows:
        return "无量化测算结果（问题未涉及冲击情景）。"
    lines = ["| 行业 | 产出变动% | 产出变动(亿元) | 直接效应 | 间接效应 | 风险评分 |",
             "|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(
            f"| {r['industry']} | {r['impact_pct']:+.2f}% | "
            f"{_fmt(r.get('delta_output_yi'))} | "
            f"{_fmt(r.get('direct_effect_yi'))} | "
            f"{_fmt(r.get('indirect_effect_yi'))} | "
            f"{r.get('risk_score', '-')} |"
        )
    return "\n".join(lines)


def build_markdown(report: dict) -> str:
    lines = [
        "# 房地产产业链风险分析报告",
        f"\n> 分析问题：**{report.get('question', '')}**  \n> 综合风险评分：**{report.get('risk_score', '-')} / 100（{report.get('risk_level', '')}）**  \n> 生成时间：{report.get('created_at', '')}",
        "\n## 1. Executive Summary",
        "\n" + report.get("summary", ""),
        "\n## 2. Risk Assessment",
        f"\n- 综合风险评分：**{report.get('risk_score')}**\n- 风险等级：**{report.get('risk_level')}**",
        "\n### 行业风险评分（多指标加权模型）",
    ]
    for s in report.get("industry_scores", []):
        lines.append(f"- **{s['industry']}**：{s['risk_score']}（{s['risk_level']}）")
    lines += ["\n## 3. Transmission Mechanism（传导机制）"]
    for i, step in enumerate(report.get("transmission_path", []), 1):
        lines.append(f"{i}. {step}")
    lines += ["\n## 4. Affected Industries（影响矩阵）", "\n" + _industries_md(report.get("affected_industries", []))]
    if report.get("similar_cases"):
        lines += ["\n### 历史对比"]
        for c in report["similar_cases"]:
            lines.append(f"- **{c['title']}**：{c.get('peak_impact', '')} —— {c.get('lessons', '')}")
    lines += [
        "\n## 5. Model Explanation（模型依据）",
        "\n" + report.get("model_basis", ""),
        "\n### 数据依据",
    ]
    for d in report.get("data_basis", []):
        lines.append(f"- {d}")
    lines += ["\n## 6. Conclusion（结论与建议关注指标）"]
    for k in report.get("key_indicators", []):
        lines.append(f"- {k}")
    lines += ["\n---\n*本报告由房地产产业链风险分析智能体自动生成（LLM Agent + 投入产出模型 + 风险评分模型 + RAG知识库），仅供研究演示，不构成投资建议。*"]
    return "\n".join(lines)


def save_report(report: dict) -> str:
    md = build_markdown(report)
    path = REPORTS_DIR / f"{report['report_id']}.md"
    path.write_text(md, encoding="utf-8")
    return str(path)
