# -*- coding: utf-8 -*-
"""调试2023原始表：钢铁行数据与总投入列"""
import pandas as pd

src = r"d:\python\Financial\项目竞赛资料\北京市投入产出表\2023年北京市投入产出表.xlsx"
df = pd.read_excel(src, sheet_name="2023年北京地区投入产出表", header=None)

# 表头行4的部门列
header = df.iloc[4].tolist()
steel_col = next(j for j, v in enumerate(header) if "金属冶炼" in str(v))
print(f"表头[金属冶炼和压延加工品]列号: {steel_col}")

# 数据行（列1部门名）
for i in range(6, 20):
    n = df.iloc[i, 1]
    if pd.notna(n) and "金属" in str(n):
        print(f"\n行{i} [{n}]:")
        print("  列0:", df.iloc[i, 0], "| 列1:", n, "| 列2:", df.iloc[i, 2])
        print("  列3-8:", df.iloc[i, 3:9].tolist())
        print("  自身列(steel_col):", df.iloc[i, steel_col])

# 总投入行
for i in range(len(df)-1, 40, -1):
    if pd.notna(df.iloc[i, 0]) and "总投入" in str(df.iloc[i, 0]):
        print(f"\n总投入行{i}, 钢铁列值:", df.iloc[i, steel_col])
        break

# 行4表头前12列 + 行5
print("\n行4前12列:", [str(v).strip()[:14] for v in df.iloc[4, :12].tolist()])
print("行5前12列:", [str(v).strip()[:14] for v in df.iloc[5, :12].tolist()])
print("行6前12列:", [str(v).strip()[:14] for v in df.iloc[6, :12].tolist()])
