# -*- coding: utf-8 -*-
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

fig, ax = plt.subplots(figsize=(11, 4.6), dpi=300)
ax.axis("off")

stages = [
    ("直接冲击期", "0-6个月", "商票逾期 - 应付账款 -\n供应商坏账计提", "建筑·建材·装饰", "#ef4444", "#fee2e2"),
    ("深度传导期", "6-24个月", "停工 - 钢铁水泥需求下降\n销售 - 家电家具消费缺失", "钢铁·机械·家电·家具", "#f97316", "#ffedd5"),
    ("存量重构期", "24个月以上", "出清 - 集中度提升\n存量更新成为新需求", "专业服务·流通", "#22c55e", "#dcfce7"),
]

ax.annotate("", xy=(0.97, 0.62), xytext=(0.03, 0.62), arrowprops=dict(arrowstyle="-|>", color="#334155", lw=2))
ax.text(0.985, 0.615, "时间", fontsize=10, va="center", color="#334155")
xs = [0.13, 0.50, 0.87]
for (name, win, mech, inds, color, bg), cx in zip(stages, xs):
    ax.plot(cx, 0.62, "o", color=color, markersize=13, zorder=5)
    ax.plot(cx, 0.62, "o", color="white", markersize=6, zorder=6)
    ax.text(cx, 0.72, win, ha="center", fontsize=10.5, color=color, fontweight="bold")
    box_y, box_h = 0.18, 0.34
    ax.add_patch(plt.Rectangle((cx - 0.145, box_y), 0.29, box_h, facecolor=bg, edgecolor=color, linewidth=1.4, zorder=2))
    ax.text(cx, box_y + box_h - 0.055, name, ha="center", fontsize=12, color=color, fontweight="bold", zorder=3)
    ax.text(cx, box_y + box_h - 0.145, mech, ha="center", va="center", fontsize=9, color="#334155", zorder=3)
    ax.text(cx, box_y + 0.035, "重点行业：" + inds, ha="center", fontsize=8.5, color="#64748b", zorder=3)
ax.text(0.5, 0.03, "需求侧三阶段框架来源：恒大、融创、碧桂园、金科、世茂、阳光城六案例归纳（系统同时设供给侧供给约束框架）", ha="center", fontsize=8.5, color="#94a3b8")
ax.set_xlim(0, 1)
ax.set_ylim(0, 0.85)
ax.set_title("图3  房地产需求侧风险三阶段传导时间轴", fontsize=13, pad=8)
from pathlib import Path
out = Path(r"d:\python\Financial\docs\figures\fig3_stages.png")
out.parent.mkdir(exist_ok=True)
fig.savefig(out, bbox_inches="tight")
print("fig3 saved:", out)