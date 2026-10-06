# -*- coding: utf-8 -*-
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

fig, ax = plt.subplots(figsize=(9.6, 6.4), dpi=300)
ax.axis("off")

def box(x, y, w, h, text, fc="#eff6ff", ec="#3b82f6", fs=10, tc="#1e293b"):
    ax.add_patch(plt.Rectangle((x, y), w, h, facecolor=fc, edgecolor=ec, linewidth=1.4, zorder=2))
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=fs, color=tc, zorder=3)

def arrow(x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1), arrowprops=dict(arrowstyle="-|>", color="#475569", lw=1.4))

SUPM = "$^{-1}$"
D = chr(0x0394)
LEON = "Leontief 需求侧模型\n" + D + "X=(I-A)" + SUPM + D + "Y"
GHOSH = "Ghosh 供给侧模型\n" + D + "X=" + D + "V(I-B)" + SUPM + ", B=D" + SUPM + "Z"

box(0.34, 0.88, 0.32, 0.09, "用户问题 / 风险事件", fc="#fef2f2", ec="#ef4444")
arrow(0.5, 0.88, 0.5, 0.815)
box(0.30, 0.72, 0.40, 0.095, "冲击性质识别（服务端守卫）", fc="#eff6ff")
arrow(0.38, 0.72, 0.17, 0.63)
arrow(0.50, 0.72, 0.50, 0.63)
arrow(0.62, 0.72, 0.83, 0.63)
box(0.02, 0.52, 0.30, 0.11, "需求数量冲击\n（投资/销售/新开工）", fc="#dbeafe", ec="#2563eb")
box(0.35, 0.52, 0.30, 0.11, "供给数量冲击\n（初始投入收缩/减产）", fc="#dbeafe", ec="#2563eb")
box(0.68, 0.52, 0.30, 0.11, "价格与资产价格\n（涨价/房价变动）", fc="#fef9c3", ec="#ca8a04")
arrow(0.17, 0.52, 0.17, 0.435)
arrow(0.50, 0.52, 0.50, 0.435)
arrow(0.83, 0.52, 0.83, 0.435)
box(0.02, 0.325, 0.30, 0.11, LEON, fc="#1e40af", ec="#1e3a8a", fs=9.5, tc="#ffffff")
box(0.35, 0.325, 0.30, 0.11, GHOSH, fc="#1e40af", ec="#1e3a8a", fs=9.5, tc="#ffffff")
box(0.68, 0.325, 0.30, 0.11, "定性机制分析\n（财富效应/抵押品/成本渠道）", fc="#f1f5f9", ec="#64748b", fs=9)
arrow(0.17, 0.325, 0.42, 0.245)
arrow(0.50, 0.325, 0.52, 0.245)
arrow(0.83, 0.325, 0.62, 0.245)
box(0.30, 0.135, 0.40, 0.11, "产业关联压力 - 情景风险评分\n（代理变量口径·横向压力比较）", fc="#dcfce7", ec="#16a34a")
arrow(0.5, 0.135, 0.5, 0.075)
box(0.25, -0.005, 0.50, 0.08, "月度数据 + 历史案例验证 - 三阶段风险判断 - 智能体报告", fc="#fef2f2", ec="#ef4444", fs=9.5)
ax.set_xlim(0, 1)
ax.set_ylim(-0.03, 1.0)
ax.set_title("图2  项目总体研究思路与模型分流框架", fontsize=13, pad=10)
from pathlib import Path
out = Path(r"d:\python\Financial\docs\figures\fig2_framework.png")
out.parent.mkdir(exist_ok=True)
fig.savefig(out, bbox_inches="tight")
print("fig2 saved:", out)