# -*- coding: utf-8 -*-
"""修复 macro_monthly.json 断点：
1. 每年12月缺失（统计局不单独发布）→ 用11月值插补（累计同比口径 12月≈11月）
2. 1月 null（水泥/玻璃春节停报）→ 前后两月均值
"""
import json
from datetime import datetime
from pathlib import Path

p = Path(r"d:\python\Financial\backend\app\data\macro_monthly.json")
data = json.loads(p.read_text(encoding="utf-8"))


def month_add(m: str, k: int) -> str:
    d = datetime.strptime(m, "%Y-%m")
    y, mo = d.year + (d.month - 1 + k) // 12, (d.month - 1 + k) % 12 + 1
    return f"{y}-{mo:02d}"


for key, series in data["series"].items():
    # ① 每年12月/次年1月缺失（统计局12月不单发、1-2月合并发布）→ 用邻月值插补
    for y in [f"20{yy}" for yy in range(21, 27)]:
        for miss, neighbor in [(f"{y}-12", f"{y}-11"), (f"{y}-01", f"{y}-02")]:
            if miss not in series and neighbor in series and series[neighbor] is not None:
                series[miss] = series[neighbor]
    # ② null → 前后均值（无后者用前者）
    for m in sorted(series):
        if series[m] is None:
            prev_k, next_k = month_add(m, -1), month_add(m, 1)
            prev_v = series.get(prev_k)
            next_v = series.get(next_k)
            if prev_v is not None and next_v is not None:
                series[m] = round((prev_v + next_v) / 2, 2)
            elif prev_v is not None:
                series[m] = prev_v
            elif next_v is not None:
                series[m] = next_v
    data["series"][key] = dict(sorted(series.items()))

# 末端统一：截掉部分序列多出的尾部月（对齐长度用，图上以最长为准即可，不截也不影响）
p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

# 验证
for key, s in data["series"].items():
    ms = [datetime.strptime(m, "%Y-%m") for m in sorted(s)]
    bad = [(a.strftime("%Y-%m"), b.strftime("%Y-%m")) for a, b in zip(ms, ms[1:])
           if (b.year * 12 + b.month) - (a.year * 12 + a.month) != 1]
    nulls = [m for m, v in s.items() if v is None]
    status = "连续无null" if not bad and not nulls else f"断档={bad} nulls={nulls}"
    print(f"{key}: {status} | {sorted(s)[0]} ~ {sorted(s)[-1]} ({len(s)}期)")
