# -*- coding: utf-8 -*-
"""从北京2017年42部门投入产出表提取并聚合 A 矩阵 → 替换 backend/app/data/io_table.json
步骤：
1. 定位中间流量矩阵（42×42）、最终使用合计列、总投入行
2. 按映射规则聚合到系统13部门（真实可映射口径）
3. A = 聚合流量 / 聚合总投入（列归一化），单位统一为亿元
4. 写入 io_table.json（保留 debt_ratio，部门名适配）
"""
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

SRC = r"d:\python\Financial\项目竞赛资料\北京市投入产出表\2017年北京市投入产出表.xls"
DST = Path(r"d:\python\Financial\backend\app\data\io_table.json")
UNIT = 1e4  # 万元 → 亿元

# 系统13部门 ← 北京42部门聚合映射（部门名精确匹配，带模糊兜底）
MAPPING = {
    "房地产": ["房地产"],
    "建筑业": ["建筑"],
    "钢铁": ["金属矿采选产品", "金属冶炼和压延加工品", "金属制品"],
    "建材": ["非金属矿和其他矿采选产品", "非金属矿物制品"],
    "化工": ["石油和天然气开采产品", "石油、炼焦产品和核燃料加工品", "化学产品"],
    "机械设备": ["通用设备", "专用设备", "交通运输设备", "通信设备、计算机和其他电子设备",
               "仪器仪表", "金属制品、机械和设备修理服务", "其他制造产品和废品废料"],
    "家用电器": ["电气机械和器材"],
    "家具制造": ["木材加工品和家具"],
    "金融业": ["金融"],
    "批发零售": ["批发和零售"],
    "交通运输": ["交通运输、仓储和邮政"],
    "电力热力": ["煤炭采选产品", "电力、热力的生产和供应", "燃气生产和供应", "水的生产和供应"],
    "专业服务": ["农林牧渔产品和服务", "食品和烟草", "纺织品", "纺织服装鞋帽皮革羽绒及其制品",
               "造纸印刷和文教体育用品", "住宿和餐饮", "信息传输、软件和信息技术服务",
               "租赁和商务服务", "研究和试验发展", "综合技术服务", "水利、环境和公共设施管理",
               "居民服务、修理和其他服务", "教育", "卫生和社会工作", "文化、体育和娱乐",
               "公共管理、社会保障和社会组织"],
}

df = pd.read_excel(SRC, header=None)

# ---- 1. 定位42部门列（行6的连续部门名）----
row6 = df.iloc[6].tolist()
sector_cols = []  # (col_idx, name)
for j, v in enumerate(row6):
    if pd.notna(v) and str(v).strip() and j >= 3 and str(v).strip() not in ("代码", "中间使用", "产出"):
        sector_cols.append((j, str(v).strip()))
        if len(sector_cols) == 42:
            break
assert len(sector_cols) == 42, f"部门列数量异常: {len(sector_cols)}"
col_names = [n for _, n in sector_cols]
col_idx = [j for j, _ in sector_cols]
print(f"42部门列: {col_idx[0]}~{col_idx[-1]}，首={col_names[0]} 末={col_names[-1]}")

# ---- 2. 定位最终使用合计列 ----
fin_col = None
for j, v in enumerate(row6):
    if pd.notna(v) and str(v).strip() == "最终使用合计":
        fin_col = j
        break
assert fin_col, "未找到[最终使用合计]列"
print(f"最终使用合计列: {fin_col}")

# ---- 3. 定位42部门行（行10起，行标签在列1）与总投入行 ----
row_sectors = []  # (row_idx, name)
for i in range(7, 59):
    v = df.iloc[i, 1]
    if pd.notna(v) and str(v).strip() in col_names:
        row_sectors.append((i, str(v).strip()))
# 按表内出现顺序对齐
row_map = {}
for i, n in row_sectors:
    if n not in row_map:
        row_map[n] = i
assert len(row_map) == 42, f"部门行数量异常: {len(row_map)}"

total_in_row = None
for i in range(50, 60):
    if pd.notna(df.iloc[i, 0]) and str(df.iloc[i, 0]).strip() == "总投入":
        total_in_row = i
        break
assert total_in_row, "未找到[总投入]行"
print(f"总投入行: {total_in_row}")

# ---- 4. 提取矩阵（万元）----
Z = np.zeros((42, 42))     # 中间流量
Y = np.zeros(42)           # 最终使用合计
X = np.zeros(42)           # 总投入(=总产出)
for a, name_a in enumerate(col_names):
    ri = row_map[name_a]
    Y[a] = float(pd.to_numeric(df.iloc[ri, fin_col], errors="coerce") or 0)
    X[a] = float(pd.to_numeric(df.iloc[total_in_row, col_idx[a]], errors="coerce") or 0)
    for b in range(42):
        Z[a, b] = float(pd.to_numeric(df.iloc[ri, col_idx[b]], errors="coerce") or 0)
print(f"总产出合计: {X.sum()/UNIT:,.0f} 亿元")

# ---- 5. 聚合到系统13部门 ----
target_names = list(MAPPING.keys())
# 42部门名 → 聚合组索引
assign = {}
for tgt, srcs in MAPPING.items():
    for s in srcs:
        matched = [c for c in col_names if c == s]
        if not matched:
            raise SystemExit(f"映射失败: 表中无部门[{s}]")
        for m in matched:
            assign[m] = target_names.index(tgt)
assert len(assign) == 42

N = len(target_names)
g = np.array([assign[c] for c in col_names])
Zt, Yt, Xt = np.zeros((N, N)), np.zeros(N), np.zeros(N)
for I in range(N):
    mask_i = g == I
    for J in range(N):
        Zt[I, J] = Z[np.ix_(mask_i, g == J)].sum()
np.add.at(Yt, g, Y)
np.add.at(Xt, g, X)

# A = 聚合流量 / 聚合总投入（列归一化）
A = Zt / np.where(Xt[None, :] > 0, Xt[None, :], np.inf)

# ---- 6. 写入 io_table.json ----
DEBT = {"房地产": 78, "建筑业": 70, "钢铁": 55, "建材": 58, "化工": 55, "机械设备": 55,
        "家用电器": 50, "家具制造": 50, "金融业": 92, "批发零售": 60, "交通运输": 58,
        "电力热力": 65, "专业服务": 45}
data = {
    "metadata": {
        "source": "北京市2017年投入产出表（42部门基本流量表，当年生产者价格）",
        "aggregation": "42部门按产业链口径聚合为13部门",
        "unit": "亿元（原始表万元/1e4）",
        "method": "A_ij = 聚合中间流量 / 聚合总投入（直接消耗系数，列归一化）",
    },
    "sectors": [{"code": f"S{i+1:02d}", "name": n} for i, n in enumerate(target_names)],
    "A": [[round(float(A[i][j]), 5) for j in range(N)] for i in range(N)],
    "base_output": [round(float(v) / UNIT, 1) for v in Xt],
    "base_final_demand": [round(float(v) / UNIT, 1) for v in Yt],
    "debt_ratio": DEBT,
}
backup = DST.with_suffix(".json.bak_demo")
if not backup.exists():
    backup.write_text(DST.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"原演示数据已备份: {backup.name}")
DST.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"已写入 {DST}")

# ---- 7. 验证 ----
A2 = np.array(data["A"])
L = np.linalg.inv(np.eye(N) - A2)
mult = L.sum(axis=0)
print("\n各部门影响力乘数（后向联动）:")
for i, n in enumerate(target_names):
    print(f"  {n}: {mult[i]:.3f}")
re_i = target_names.index("房地产")
print(f"\n房地产冲击验证（最终需求-10%情景, dX = L @ dY）:")
dY = np.zeros(N)
dY[re_i] = -0.10 * Yt[re_i] / UNIT
dX = L @ dY
for i in np.argsort(np.abs(dX))[::-1][:5]:
    print(f"  {target_names[i]}: {dX[i]:+,.0f} 亿元 ({dX[i]/(Xt[i]/UNIT)*100:+.2f}%)")
