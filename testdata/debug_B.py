# -*- coding: utf-8 -*-
"""调试 B 矩阵病态原因"""
import sys
sys.path.insert(0, r"d:\python\Financial\backend")
import numpy as np
from app.models import input_output as io

Z = io.A * io.X_BASE[None, :]
row_sums = Z.sum(axis=1)
print("各部门行和（中间使用合计，亿元）:")
for i, (n, s) in enumerate(zip(io.SECTOR_NAMES, row_sums)):
    flag = " ←← 异常" if s <= 0 else ""
    print(f"  {n}: {s:.1f}{flag}")

B = Z / np.where(row_sums[:, None] > 0, row_sums[:, None], np.inf)
B = np.nan_to_num(B)
print("\nB 行和范围:", B.sum(axis=1).min(), "~", B.sum(axis=1).max())
I_B = np.eye(io.N) - B
cond = np.linalg.cond(I_B)
print("(I-B) 条件数:", cond)
det = np.linalg.det(I_B)
print("(I-B) 行列式:", det)
