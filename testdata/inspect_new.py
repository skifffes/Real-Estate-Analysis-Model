# -*- coding: utf-8 -*-
"""探测 2023/2020/2012系数表 结构"""
import pandas as pd
from pathlib import Path

BASE = Path(r"d:\python\Financial\项目竞赛资料\北京市投入产出表")

def dump(path, sheet, rows):
    df = pd.read_excel(path, sheet_name=sheet, header=None)
    print(f"=== {Path(path).name} [{sheet}] shape={df.shape} ===")
    for i in rows:
        row = df.iloc[i].tolist()
        vals = [str(v).strip()[:12] for v in row[:10] if pd.notna(v)]
        print(f"行{i}: {vals}")

# 2023: 部门名行约4
p = BASE / "2023年北京市投入产出表.xlsx"
df = pd.read_excel(p, sheet_name="2023年北京地区投入产出表", header=None)
print("=== 2023 表 行3-8 前8列 ===")
for i in range(3, 9):
    print(f"行{i}:", [str(v).strip()[:14] for v in df.iloc[i, :8].tolist()])
# 部门名行
r4 = df.iloc[4].tolist()
names = [(j, str(v).strip()) for j, v in enumerate(r4) if pd.notna(v) and len(str(v).strip()) > 1]
print("行4全部非空:", names[:8], "... 共", len(names))

# 2020: 部门名行约4
p = BASE / "2020年北京市投入产出表.xlsx"
df = pd.read_excel(p, sheet_name="Sheet1", header=None)
print("\n=== 2020 表 行2-7 前8列 ===")
for i in range(2, 8):
    print(f"行{i}:", [str(v).strip()[:14] for v in df.iloc[i, :8].tolist()])
r4 = df.iloc[4].tolist()
names = [(j, str(v).strip()) for j, v in enumerate(r4) if pd.notna(v) and len(str(v).strip()) > 1]
print("行4全部非空:", names[:8], "... 共", len(names))

# 2012: 直接消耗系数表
p = BASE / "2012年北京市投入产出表.xls"
dump(p, "直接消耗系数", [4, 5, 6, 7, 8])
df = pd.read_excel(p, sheet_name="直接消耗系数", header=None)
r = df.iloc[6].tolist()
names = [(j, str(v).strip()) for j, v in enumerate(r) if pd.notna(v) and len(str(v).strip()) > 1]
print("系数表行6非空数:", len(names), names[:5])
