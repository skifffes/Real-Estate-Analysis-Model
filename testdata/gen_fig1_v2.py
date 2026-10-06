# -*- coding: utf-8 -*-
from pathlib import Path
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei"]
plt.rcParams["axes.unicode_minus"] = False

multi = json.loads(Path(r"d:\python\Financial\backend\app\data\io_multiyear.json").read_text(encoding="utf-8"))
m12 = multi["multipliers"]["2012"]
m17 = multi["multipliers"]["2017"]
m23 = multi["multipliers"]["2023"]

sectors = ["房地产", "建筑业", "钢铁", "建材", "家用电器", "专业服务", "金融业"]
v12 = [m12[s] for s in sectors]
v17 = [m17[s] for s in sectors]
v23 = [m23[s] for s in sectors]

fig, ax = plt.subplots(figsize=(10, 5.2), dpi=300)
x = np.arange(len(sectors))
w = 0.26
b1 = ax.bar(x - w, v12, w, label="2012年", color="#9ca3af")
b2 = ax.bar(x, v17, w, label="2017年", color="#60a5fa")
b3 = ax.bar(x + w, v23, w, label="2023年", color="#1d4ed8")
for bars in (b1, b2, b3):
    for b in bars:
        ax.annotate(f"{b.get_height():.2f}", (b.get_x() + b.get_width() / 2, b.get_height()), ha="center", va="bottom", fontsize=7.5, color="#374151")
ax.annotate(f"{m23['房地产']:.2f}", (x[0] + w, m23["房地产"]), ha="center", va="bottom", fontsize=8.5, color="#111827", fontweight="bold")
ax.set_ylabel("影响力乘数（后向联动）", fontsize=11)
ax.set_title("图1  北京市主要行业影响力乘数演变（2012 / 2017 / 2023）", fontsize=13, pad=12)
ax.set_xticks(x)
ax.set_xticklabels(sectors, fontsize=10.5)
ax.legend(fontsize=10, frameon=False, ncol=3, loc="upper right")
ax.spines[["top", "right"]].set_visible(False)
ax.set_ylim(0, 5.9)
ax.text(0.99, -0.13, "注：房地产乘数在三个年份均低于建筑业、钢铁与建材。", transform=ax.transAxes, ha="right", fontsize=9, color="#6b7280")
out = Path(r"d:\python\Financial\docs\figures\fig1_multiplier.png")
fig.savefig(out, bbox_inches="tight")
print("fig1 v2 saved")