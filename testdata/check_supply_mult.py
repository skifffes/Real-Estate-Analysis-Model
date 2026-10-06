# -*- coding: utf-8 -*-
"""独立核查钢铁供给乘数 30.73 是否正确"""
import sys
sys.path.insert(0, r"d:\python\Financial\backend")
import numpy as np
from app.models import input_output as io

Z = io.A * io.X_BASE[None, :]
D = np.diag(io.X_BASE)
B = np.linalg.inv(D) @ Z
G = np.linalg.inv(np.eye(io.N) - B)
j = io.SECTOR_NAMES.index("钢铁")

print("钢铁 G 第j行（各下游的Ghosh传导系数）:")
row = G[j, :]
for i in np.argsort(-row)[:8]:
    print(f"  {io.SECTOR_NAMES[i]}: {row[i]:.3f}")
print(f"行合计（供给乘数）: {row.sum():.2f}")

# 与反馈对照：钢铁增加值-10% => -355亿
VA = io.X_BASE - (io.A * io.X_BASE[None, :]).sum(axis=0)
print(f"\n钢铁增加值: {VA[j]:.1f} 亿 | -10% => ΔV={-0.1*VA[j]:.2f}")
print(f"总变动: {(-0.1*VA[j]) * row.sum():.1f} 亿元（反馈说约-355）")

# 检查B的对角与行特征
print(f"\nB对角线(钢铁): {B[j,j]:.3f}")
print(f"B行和(钢铁): {B[j].sum():.3f}")
print(f"ρ(B): {max(abs(np.linalg.eigvals(B))):.4f}")
