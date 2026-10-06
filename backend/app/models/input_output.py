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
        "transmission_stages": _stage_forecast(rows, shock_percent, direction),
    }


def _stage_forecast(rows: list, shock_pct: float, direction: str, kind: str = "demand") -> dict:
    """传导三阶段预判：需求侧用六案例归纳框架，供给侧用成本推动框架"""
    import json as _json
    from ..config import DATA_DIR as _DD
    try:
        fw = _json.loads((_DD / "transmission_stages.json").read_text(encoding="utf-8"))
    except Exception:
        return {}
    stage_list = fw.get("stages_supply") if kind == "supply" else fw.get("stages")
    if not stage_list:
        return {}
    impact_by_ind = {r["industry"]: r["impact_pct"] for r in rows}
    severity = min(abs(shock_pct) / 30.0, 1.0)  # 冲击幅度 → 严重度 0~1
    stages = []
    for st in stage_list:
        # 各阶段命中行业 × 该行业受冲击幅度 → 阶段压力分（0~100）
        hits = []
        for ind in st["hit_industries"]:
            p = impact_by_ind.get(ind)
            if p is not None:
                hits.append({"industry": ind, "impact_pct": p})
        pressure = min(100, round(severity * st["hit_hardness"] / 3 * 100
                                  + sum(abs(h["impact_pct"]) for h in hits) / max(len(hits), 1) * 3))
        stages.append({
            "name": st["name"], "window": st["window"],
            "mechanism": st["mechanism"], "channels": st["channels"],
            "hit_industries": st["hit_industries"],
            "verify_indicators": st["verify_indicators"],
            "case_evidence": st["case_evidence"],
            "pressure": pressure,
        })
    return {"framework": fw["framework"], "source": fw["source"],
            "cross_case_rules": fw["cross_case_rules"], "stages": stages}


def ghosh_supply_shock(shock_sector: str, shock_percent: float, direction: str = "下降") -> dict:
    """Ghosh-type 供给侧冲击模型（地区表适配口径，一轮直接分配）
    ΔX_k = (x_jk / TI_k) × ΔV_j 的投入依赖度等比传导。

    为什么不用标准 Ghosh (I-B)^(-1)：地区投入产出表的中间流量含调入品
    （如北京钢铁需求主要靠河北调入），B_ij=Z_ij/X_i 的行和可达 4+，
    (I-B) 谱半径>1 幂级数不收敛（实测奇异）。一轮直接分配规避调入因素，
    是地区表供给侧传导的常用可辩护口径。"""
    if shock_sector not in SECTOR_NAMES:
        return {"error": f"未知部门: {shock_sector}"}
    j = SECTOR_NAMES.index(shock_sector)
    sign = -1.0 if direction in ("下降", "下跌", "减产", "回落") else 1.0

    Z = A * X_BASE[None, :]                          # 中间流量矩阵（亿元，含调入）
    TI = Z.sum(axis=0)                               # 各部门中间投入合计（列和）
    dX_j = sign * (shock_percent / 100.0) * X_BASE[j]  # 冲击部门自身产出变动

    # 冲击部门对各部门的分配比例（含最终使用，基于总使用结构）
    total_use = Z.sum(axis=1) + np.array(Y_BASE)     # 部门i产品的总使用
    alloc = Z[j, :] / np.where(total_use > 0, total_use, np.inf)  # 分配给各部门的比例
    alloc = np.nan_to_num(alloc)

    # 一轮直接分配传导：下游k从冲击部门获得的中间投入减少 alloc[k]*|dX_j|，
    # 按其对该投入的依赖度（占中间投入合计比例）等比压缩产出
    rows = []
    for k, name in enumerate(SECTOR_NAMES):
        if k == j:
            continue
        cut = alloc[k] * abs(dX_j)                   # k 获得的中间品减少量
        if cut <= 0 or TI[k] <= 0:
            continue
        dX_k = -cut / TI[k] * X_BASE[k]              # 产出等比收缩
        impact_pct = float(dX_k / X_BASE[k] * 100.0)
        if abs(impact_pct) < 0.05:
            continue
        rows.append({"industry": name, "impact_pct": round(impact_pct, 2),
                     "delta_output_yi": round(float(dX_k), 1),
                     "debt_ratio": DEBT.get(name, 55)})

    rows.sort(key=lambda r: abs(r["impact_pct"]), reverse=True)
    total_delta = dX_j + sum(r["delta_output_yi"] for r in rows)
    supply_mult = abs(sum(r["delta_output_yi"] for r in rows)) / max(abs(dX_j), 1e-9)

    return {
        "model": "Ghosh-type Supply-Side Model (regional direct allocation)",
        "scenario": f"{shock_sector}供给侧（产出）{direction} {shock_percent}%",
        "sector_order": SECTOR_NAMES,
        "impact_matrix": rows,
        "total_output_change_yi": round(total_delta, 1),
        "transmission_stages": _stage_forecast(rows, shock_percent, direction, kind="supply"),
        "total_output_change_pct": round(total_delta / float(X_BASE.sum()) * 100, 3),
        "real_estate_multiplier": round(impact_multiplier(A, SECTOR_NAMES.index("房地产")), 2),
        "construction_multiplier": round(impact_multiplier(A, SECTOR_NAMES.index("建筑业")), 2),
        "supply_multiplier": round(1 + supply_mult, 2),
        "note": "地区表适配口径：中间流量含调入品，标准Ghosh(I-B)^(-1)在地区表上谱半径>1不收敛，"
                "故采用一轮直接分配（供给缩减按分配结构等比传导至下游），调入效应留作展望",
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
