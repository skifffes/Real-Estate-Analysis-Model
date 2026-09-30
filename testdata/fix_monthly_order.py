# -*- coding: utf-8 -*-
"""修复 macro_monthly.json 序列顺序（升序 2021-10 → 2026-08）"""
import json
from pathlib import Path

p = Path(r"d:\python\Financial\backend\app\data\macro_monthly.json")
data = json.loads(p.read_text(encoding="utf-8"))
for k, v in data["series"].items():
    data["series"][k] = dict(sorted(v.items()))
p.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

s = data["series"]["新开工同比"]
items = list(s.items())
print("修复后 新开工 首2期:", items[:2], "末3期:", items[-3:])
