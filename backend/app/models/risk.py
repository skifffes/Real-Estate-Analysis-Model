"""Tool 2: 风险评分模型（0-100，多指标加权）"""
import math


def _clamp(v, lo=0.0, hi=100.0):
    return max(lo, min(hi, v))


def _sub_score(x, worst, best):
    """线性归一化到 0-100（x=worst → 100分，x=best → 0分，越接近 worst 风险越高）"""
    if x is None:
        return 50.0
    if best == worst:
        return 50.0
    return _clamp((best - x) / (best - worst) * 100.0)


def risk_level(score: float) -> str:
    if score >= 75:
        return "极高"
    if score >= 60:
        return "高"
    if score >= 45:
        return "中"
    if score >= 30:
        return "关注"
    return "低"


def compute_risk_score(revenue_change: float, debt_ratio: float,
                       cash_flow_change: float, market_change: float) -> dict:
    """
    revenue_change:  收入同比变化%（如 -10）
    debt_ratio:      资产负债率%（如 78）
    cash_flow_change:经营现金流变化%（如 -20）
    market_change:   市场需求/价格变化%（如 -12）
    """
    s_revenue = _sub_score(revenue_change, worst=-30, best=10)
    s_debt = _sub_score(debt_ratio, worst=95, best=35)
    s_cash = _sub_score(cash_flow_change, worst=-40, best=15)
    s_market = _sub_score(market_change, worst=-30, best=10)

    # 权重：收入与债务为主，现金流与市场为辅
    score = (0.30 * s_revenue + 0.30 * s_debt
             + 0.20 * s_cash + 0.20 * s_market)
    score = round(_clamp(score), 1)
    return {
        "risk_score": score,
        "risk_level": risk_level(score),
        "components": {
            "收入压力": round(s_revenue, 1),
            "债务压力": round(s_debt, 1),
            "现金流压力": round(s_cash, 1),
            "市场需求压力": round(s_market, 1),
        },
        "weights": {"收入": 0.30, "债务": 0.30, "现金流": 0.20, "市场需求": 0.20},
    }


def industry_risk_from_impact(industry: str, impact_pct: float, debt_ratio: float) -> dict:
    """由产业链冲击结果推导行业风险评分"""
    return compute_risk_score(
        revenue_change=impact_pct,          # 产出变动近似收入变动
        debt_ratio=debt_ratio,
        cash_flow_change=impact_pct * 1.5,  # 现金流波动放大
        market_change=impact_pct * 0.8,
    )


def aggregate_risk(industry_scores: list[dict]) -> dict:
    """行业风险 → 系统性综合风险（取加权高分，强调尾部风险）"""
    if not industry_scores:
        return {"risk_score": 0, "risk_level": "低"}
    scores = [s["risk_score"] for s in industry_scores]
    top = sorted(scores, reverse=True)[:3]
    mean = sum(scores) / len(scores)
    # 均值 + 尾部溢价，突出高风险行业的主导作用
    agg = round(_clamp(mean * 0.6 + (sum(top) / len(top)) * 0.4), 1)
    return {"risk_score": agg, "risk_level": risk_level(agg)}
