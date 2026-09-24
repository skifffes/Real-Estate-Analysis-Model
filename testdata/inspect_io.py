# -*- coding: utf-8 -*-
"""定位投入产出表的部门行/最终需求列/总投入行"""
import pandas as pd

src = r"d:\python\Financial\项目竞赛资料\北京市投入产出表\2017年北京市投入产出表.xls"
df = pd.read_excel(src, header=None)

# 列6行的部门名（中间使用起始），找42部门范围
col_names = df.iloc[6].tolist()
print("列6部门名前5:", [c for c in col_names[3:9]])
print("列6部门名尾5:", [c for c in col_names[-8:]])

# 行标签（第0列）全部非空值
for i in range(6, 59):
    v = df.iloc[i, 0]
    if pd.notna(v) and str(v).strip():
        print(f"行{i}: {str(v).strip()[:24]!r}", " | 列1代码:", df.iloc[i, 1])
