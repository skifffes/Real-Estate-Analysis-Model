# -*- coding: utf-8 -*-
"""调试最终使用列提取与钢铁行的行平衡"""
import pandas as pd

src = r"d:\python\Financial\项目竞赛资料\北京市投入产出表\2023年北京市投入产出表.xlsx"
df = pd.read_excel(src, sheet_name="2023年北京地区投入产出表", header=None)
print("shape:", df.shape)

# 行4 所有含关键词的列
print("\n行4 相关表头列:")
for j, v in enumerate(df.iloc[4].tolist()):
    s = str(v).strip()
    if s and any(k in s for k in ("最终", "合计", "流出", "流入", "进口", "误差", "使用")):
        print(f"  列{j}: {s[:30]}")

# 金属冶炼行（行19）列 44~59
print("\n金属冶炼行19 列44~59:")
for j in range(44, min(60, df.shape[1])):
    v = df.iloc[19, j]
    h = str(df.iloc[4, j]).strip()[:18] if pd.notna(df.iloc[4, j]) else "nan"
    print(f"  列{j} [{h}]: {v if pd.notna(v) else '·'}")
