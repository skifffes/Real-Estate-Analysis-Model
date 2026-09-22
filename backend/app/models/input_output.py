"""Tool 1: 产业链影响分析 —— 列昂惕夫投入产出模型 X = (I-A)^(-1) Y"""
import json
import numpy as np

from ..config import DATA_DIR

_IO = json.loads((DATA_DIR / "io_table.json").read_text(encoding="utf-8"))
SECTOR_NAMES = [s["name"] for s in _IO["sectors"]]
A = np.array(_IO["A"], dtype=float)
X_BASE = np.array(_IO["base_output"], dtype=float)
Y_BASE = np.array(_IO["base_final_demand"], dtype=float)
DEBT = _IO["debt_ratio"]
N = len(SECTOR_NAMES)

# 房地产投资冲击直接作用的部门（资本形成端）
RE_SECTORS = ["房地产", "建筑业"]


def leontief_inverse(a: np.ndarray) -> np.ndarray:
    """完全需求系数矩阵 L = (I - A)^(-1)"""
    return np.linalg.inv(np.eye(len(a)) - a)


def impact_multiplier(a: np.ndarray, j: int) -> float:
    """部门j最终需求变动1单位对总产出的拉动（后向联动乘数）"""
    return float(leontief_inverse(a)[:, j].sum())


def analyze_shock(shock_percent: float, direction: str = "下降",
                  shock_sectors=None) -> dict:
    """
    房地产冲击的产业链影响矩阵。
    shock_percent: 冲击幅度（正数，如15表示15%）
    direction: "下降" 或 "上升"
    """
    sectors = shock_sectors or RE_SECTORS
    sign = -1.0 if direction in ("下降", "下跌", "回落") else 1.0
    dY = np.zeros(N)
    for s in sectors:
        if s in SECTOR_NAMES:
            i = SECTOR_NAMES.index(s)
            dY[i] = sign * (shock_percent / 100.0) * Y_BASE[i]

    L = leontief_inverse(A)
    dX = L @ dY  # 总产出变动（直接+间接）

    rows = []
    for i, name in enumerate(SECTOR_NAMES):
        impact_pct = float(dX[i] / X_BASE[i] * 100.0)
        direct = float(dY[i])
        indirect = float(dX[i] - dY[i])
        if abs(impact_pct) < 0.01 and abs(dX[i]) < 50:
            continue
        rows.append({
            "industry": name,
            "delta_output_yi": round(float(dX[i]), 1),      # 亿元
            "impact_pct": round(impact_pct, 2),              # 产出变动%
            "direct_effect_yi": round(direct, 1),
            "indirect_effect_yi": round(indirect, 1),
            "multiplier": round(float(dX[i] / dY[i]), 2) if abs(dY[i]) > 1 else None,
            "debt_ratio": DEBT.get(name, 50),
        })
    rows.sort(key=lambda r: abs(r["impact_pct"]), reverse=True)

    total_delta = float(dX.sum())
    return {
        "model": "Leontief Input-Output Model, X = (I-A)^(-1) Y",
        "scenario": f"房地产{'及建筑业' if len(sectors) > 1 else ''}最终需求{direction} {shock_percent}%",
        "sector_order": SECTOR_NAMES,
        "impact_matrix": rows,
        "total_output_change_yi": round(total_delta, 1),
        "total_output_change_pct": round(total_delta / float(X_BASE.sum()) * 100, 3),
        "real_estate_multiplier": round(impact_multiplier(A, SECTOR_NAMES.index("房地产")), 2),
        "construction_multiplier": round(impact_multiplier(A, SECTOR_NAMES.index("建筑业")), 2),
    }


def supply_chain_graph(impact: dict | None = None) -> dict:
    """生成产业链关系图（供前端 ECharts graph）"""
    nodes, links = [], []
    weight = {r["industry"]: abs(r["impact_pct"]) for r in (impact or {}).get("impact_matrix", [])}
    for i, name in enumerate(SECTOR_NAMES):
        nodes.append({
            "id": name, "name": name,
            "value": round(weight.get(name, 0), 2),
            "symbolSize": 30 + min(weight.get(name, 0) * 6, 45),
            "category": 0 if name in ("房地产", "建筑业") else 1,
        })
    for j, to in enumerate(SECTOR_NAMES):
        for i, frm in enumerate(SECTOR_NAMES):
            w = A[i][j]
            if w >= 0.03:
                links.append({"source": frm, "target": to, "value": round(float(w), 3)})
    return {"nodes": nodes, "links": links}
