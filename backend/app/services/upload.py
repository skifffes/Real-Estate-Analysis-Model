"""数据上传分析服务：CSV/Excel → 统计摘要 + 指标识别 + 风险评分"""
import pandas as pd

from ..models import risk as risk_model

INDICATOR_MAP = {  # 列名关键词 → 指标
    "收入": "revenue", "营收": "revenue", "销售额": "revenue",
    "负债率": "debt", "资产负债率": "debt",
    "现金流": "cashflow", "现金": "cashflow",
    "需求": "market", "市场": "market", "价格": "market", "房价": "market",
}


def analyze_file(path: str, filename: str) -> dict:
    df = pd.read_csv(path) if filename.lower().endswith(".csv") else pd.read_excel(path)
    summary = {
        "filename": filename,
        "shape": list(df.shape),
        "columns": list(df.columns),
        "dtypes": {c: str(t) for c, t in df.dtypes.items()},
        "missing": {c: int(v) for c, v in df.isna().sum().items() if v > 0},
        "describe": {},
    }
    num_cols = df.select_dtypes("number").columns
    for c in num_cols:
        s = df[c].dropna()
        if len(s):
            summary["describe"][c] = {
                "mean": round(float(s.mean()), 2), "std": round(float(s.std()), 2),
                "min": round(float(s.min()), 2), "max": round(float(s.max()), 2),
                "latest": round(float(s.iloc[-1]), 2) if len(s) else None,
            }

    # 识别风险指标列 → 若齐全则计算风险评分
    detected = {}
    for col in df.columns:
        for kw, tag in INDICATOR_MAP.items():
            if kw in col:
                detected[tag] = col
                break
    if {"revenue", "debt"} <= detected.keys():
        last = df.iloc[-1]
        result = risk_model.compute_risk_score(
            revenue_change=float(last[detected["revenue"]]),
            debt_ratio=float(last[detected["debt"]]),
            cash_flow_change=float(last.get(detected.get("cashflow", ""), 0)),
            market_change=float(last.get(detected.get("market", ""), 0)),
        )
        summary["risk_evaluation"] = {
            "detected_indicators": {k: str(v) for k, v in detected.items()},
            **result,
        }
    summary["analysis_note"] = (
        f"数据共 {df.shape[0]} 行 × {df.shape[1]} 列，数值列 {len(num_cols)} 个。"
        + (f"识别到风险指标并完成评分：{summary['risk_evaluation']['risk_score']}（{summary['risk_evaluation']['risk_level']}）。"
           if "risk_evaluation" in summary else "未识别到完整的风险指标列（收入/负债率等）。")
    )
    return summary
