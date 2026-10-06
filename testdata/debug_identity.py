# -*- coding: utf-8 -*-
"""检查投入产出恒等式：中间使用 + 最终使用 = 总产出"""
import sys
sys.path.insert(0, r"d:\python\Financial\backend")
import numpy as np
from app.models import input_output as io

Z = io.A * io.X_BASE[None, :]
inter_use = Z.sum(axis=1)          # 中间使用合计（行）
fin_use = np.array(io.Y_BASE)      # 最终使用
total_out = np.array(io.X_BASE)    # 总产出

print(f"{'部门':<8}{'中间使用':>12}{'最终使用':>12}{'合计':>12}{'总产出':>12}{'差(应=0)':>10}")
for i, n in enumerate(io.SECTOR_NAMES):
    diff = inter_use[i] + fin_use[i] - total_out[i]
    flag = " ←← 违反恒等式" if abs(diff) > total_out[i] * 0.05 else ""
    print(f"{n:<8}{inter_use[i]:>12.0f}{fin_use[i]:>12.0f}{inter_use[i]+fin_use[i]:>12.0f}{total_out[i]:>12.0f}{diff:>10.0f}{flag}")
