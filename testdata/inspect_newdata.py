# -*- coding: utf-8 -*-
"""抽查学弟提供的数据文件结构与规范符合度"""
import pandas as pd
from pathlib import Path

BASE = Path(r"d:\python\Financial\项目竞赛资料\传导机制部分所需数据2026年9月30日")

files = [
    "房地产开发投资完成额（近5年月度）.xlsx",
    "房屋新开工面积（近5年月度）.xlsx",
    "商品房销售额（近5年月度）.xlsx",
    "各行业资产负债率（近5年）.xlsx",
    "各行业毛利率净利率（近5年平均）.xlsx",
    "上游行业（钢铁 水泥 玻璃 建材）营收与净利增速.xlsx",
    "下游行业（白色家电装修装饰）营收与净利增速.xlsx",
    "中国_资产负债率_全行业平均值_房地产业.csv",
    "中国_个人住房贷款余额_同比增长.csv",
]
for f in files:
    p = BASE / f
    try:
        df = pd.read_excel(p) if f.endswith((".xlsx", ".xls")) else pd.read_csv(p, encoding="utf-8-sig")
        print(f"=== {f} ===")
        print(f"  shape={df.shape}, 列: {list(df.columns)[:8]}")
        # 时间范围
        time_col = df.columns[0]
        if df.shape[0] > 1:
            print(f"  首行: {df.iloc[0, :3].tolist()} | 末行: {df.iloc[-1, :3].tolist()}")
    except Exception as e:
        print(f"=== {f} === 读取失败: {type(e).__name__}: {e}")
