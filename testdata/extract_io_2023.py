# -*- coding: utf-8 -*-
"""从北京2023年投入产出表提取聚合A矩阵 → 更新 io_table.json
2023表结构：行4=部门名（列3起），行5=代码，行6起=数据行（列1部门名,列2代码,列3起数据）
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

SRC = r"d:\python\Financial\项目竞赛资料\北京市投入产出表\2023年北京市投入产出表.xlsx"
SHEET = "2023年北京地区投入产出表"
DST = Path(r"d:\python\Financial\backend\app\data\io_table.json")
UNIT = 1e4

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

df = pd.read_excel(SRC, sheet_name=SHEET, header=None)

# ---- 1. 数据行部门（行6起，列1有部门名的行）----
row_sectors = []
for i in range(6, len(df)):
    v = df.iloc[i, 1]
    if pd.notna(v) and str(v).strip() and str(v).strip() not in ("中间投入", "增加值", "总投入", "中间投入合计"):
        name = str(v).strip()
        if name in ("劳动者报酬", "生产税净额", "固定资产折旧", "营业盈余", "增加值合计"):
            break
        row_sectors.append((i, name))
print(f"数据行部门数: {len(row_sectors)}，首={row_sectors[0][1]} 末={row_sectors[-1][1]}")
names = [n for _, n in row_sectors]
assert len(names) == len(set(names)), "部门名重复"

# ---- 2. 表头部门列（行4）与汇总列 ----
header = df.iloc[4].tolist()
col_of = {}
for j, v in enumerate(header):
    if pd.notna(v):
        s = str(v).strip()
        if s and s not in col_of:
            col_of[s] = j
# 检查42部门列都有
missing = [n for n in names if n not in col_of]
assert not missing, f"表头缺部门列: {missing[:5]}"
print(f"表头部门列全部命中（{len(names)}个）")

# 最终使用合计列（找含'最终使用'的列名）
fin_col = None
for k, j in col_of.items():
    if "最终使用" in k and "合计" in k:
        fin_col = j
        break
if fin_col is None:
    for k, j in col_of.items():
        if "最终使用" in k:
            fin_col = j
            break
assert fin_col is not None, f"未找到最终使用列，可用列名: {[k for k in col_of if '最终' in k or '合计' in k]}"
print(f"最终使用列: {fin_col} ({[k for k,j in col_of.items() if j==fin_col]})")

# 总投入行（列0）
total_row = None
for i in range(len(df) - 1, 40, -1):
    if pd.notna(df.iloc[i, 0]) and str(df.iloc[i, 0]).strip() in ("总投入", "总投入合计"):
        total_row = i
        break
assert total_row, "未找到总投入行"
print(f"总投入行: {total_row}")

# ---- 3. 提取 ----
n = len(names)
Z = np.zeros((n, n))
Y = np.zeros(n)
X = np.zeros(n)
for a, (ri, name_a) in enumerate(row_sectors):
    Y[a] = float(pd.to_numeric(df.iloc[ri, fin_col], errors="coerce") or 0)
    X[a] = float(pd.to_numeric(df.iloc[total_row, col_of[name_a]], errors="coerce") or 0)
    for b, name_b in enumerate(names):
        Z[a, b] = float(pd.to_numeric(df.iloc[ri, col_of[name_b]], errors="coerce") or 0)
print(f"总产出: {X.sum()/UNIT:,.0f} 亿元 | 中间流量合计: {Z.sum()/UNIT:,.0f} 亿元")

# ---- 4. 聚合 ----
target_names = list(MAPPING.keys())
assign = {}
for tgt, srcs in MAPPING.items():
    for s in srcs:
        assert s in names, f"映射失败: 无部门 {s}"
        assign[s] = target_names.index(tgt)
assert len(assign) == n

N = len(target_names)
g = np.array([assign[c] for c in names])
Zt, Yt, Xt = np.zeros((N, N)), np.zeros(N), np.zeros(N)
for I in range(N):
    for J in range(N):
        Zt[I, J] = Z[np.ix_(g == I, g == J)].sum()
np.add.at(Yt, g, Y)
np.add.at(Xt, g, X)
A = Zt / np.where(Xt[None, :] > 0, Xt[None, :], np.inf)

# ---- 5. 写入 ----
DEBT = {"房地产": 78, "建筑业": 70, "钢铁": 55, "建材": 58, "化工": 55, "机械设备": 55,
        "家用电器": 50, "家具制造": 50, "金融业": 92, "批发零售": 60, "交通运输": 58,
        "电力热力": 65, "专业服务": 45}
data = {
    "metadata": {
        "source": "北京市2023年投入产出表（42部门，当年生产者价格）",
        "aggregation": "42部门按产业链口径聚合为13部门",
        "unit": "亿元（原始表万元/1e4）",
        "method": "A_ij = 聚合中间流量 / 聚合总投入（直接消耗系数，列归一化）",
    },
    "sectors": [{"code": f"S{i+1:02d}", "name": nm} for i, nm in enumerate(target_names)],
    "A": [[round(float(A[i][j]), 5) for j in range(N)] for i in range(N)],
    "base_output": [round(float(v) / UNIT, 1) for v in Xt],
    "base_final_demand": [round(float(v) / UNIT, 1) for v in Yt],
    "debt_ratio": DEBT,
}
DST.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"已写入 {DST}")

# ---- 6. 验证 ----
A2 = np.array(data["A"])
L = np.linalg.inv(np.eye(N) - A2)
print("\n影响力乘数:")
for i, nm in enumerate(target_names):
    print(f"  {nm}: {L[:, i].sum():.3f}")
dY = np.zeros(N)
dY[target_names.index("房地产")] = -0.10 * Yt[target_names.index("房地产")] / UNIT
dX = L @ dY
print("房地产最终需求-10%冲击:")
for i in np.argsort(np.abs(dX))[::-1][:5]:
    print(f"  {target_names[i]}: {dX[i]:+,.0f} 亿元 ({dX[i]/(Xt[i]/UNIT)*100:+.2f}%)")
