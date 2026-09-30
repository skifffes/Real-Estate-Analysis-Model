# -*- coding: utf-8 -*-
"""学弟数据综合导入（2026-09-30 数据包）
1. 真实负债率 → io_table.json 的 debt_ratio（含口径元数据）
2. 宏观月度序列 → backend/app/data/macro_monthly.json
3. 房地产财务长序列 → backend/app/data/industry_finance.json
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(r"d:\python\Financial\项目竞赛资料\传导机制部分所需数据2026年9月30日")
APP_DATA = Path(r"d:\python\Financial\backend\app\data")


def read_any(name: str) -> pd.DataFrame:
    p = BASE / name
    if p.suffix == ".csv":
        for enc in ("utf-8-sig", "gbk", "gb18030"):
            try:
                return pd.read_csv(p, encoding=enc)
            except UnicodeDecodeError:
                continue
        raise ValueError(f"编码失败: {name}")
    return pd.read_excel(p)


def wind_csv(name: str) -> pd.DataFrame:
    """Wind CSV（含5行元数据，数据倒序）→ DataFrame[date, value] 升序"""
    df = read_any(name)
    df.columns = ["日期", "值"][:len(df.columns)]
    df = df[df["日期"].astype(str).str.match(r"\d{4}-\d{2}", na=False)].copy()
    df["值"] = pd.to_numeric(df["值"], errors="coerce")
    df["日期"] = pd.to_datetime(df["日期"])
    return df.sort_values("日期").reset_index(drop=True)


# ============ 1. 真实 debt_ratio ============
print("== 1. 更新 debt_ratio ==")
# 房地产：国资委全行业口径（2023最新）
debt_re = wind_csv("中国_资产负债率_全行业平均值_房地产业.csv")
re_debt = round(float(debt_re.iloc[-1]["值"]), 1)

# 申万三级行业 → 系统部门映射（取均值）
SW = read_any("各行业资产负债率（近5年）.xlsx")
SW_AVG = SW.groupby("申万行业")["近5年资产负债率行业平均值(%)"].mean()

def sw_avg(*keys) -> float:
    return round(float(np.mean([SW_AVG[k] for k in keys])), 1)

io = json.loads((APP_DATA / "io_table.json").read_text(encoding="utf-8"))

DEBT_NEW = {
    "房地产": re_debt,                                                   # 国资委全行业 2023
    "建筑业": sw_avg("建筑装饰--装修装饰Ⅱ--装修装饰Ⅲ"),                   # 申万装修装饰
    "钢铁": sw_avg("钢铁--普钢--板材", "钢铁--普钢--长材", "钢铁--普钢--钢铁管材"),  # 普钢口径
    "建材": sw_avg("建筑材料--水泥--水泥制品", "建筑材料--水泥--水泥制造",
                 "建筑材料--玻璃玻纤--玻璃制造", "建筑材料--装修建材--防水材料",
                 "建筑材料--装修建材--管材"),                             # 核心建材三级
    "家用电器": sw_avg("家用电器--白色家电--空调", "家用电器--白色家电--冰洗",
                     "家用电器--黑色家电--彩电"),                           # 大家电口径
}
for k, v in DEBT_NEW.items():
    print(f"  {k}: {io['debt_ratio'][k]} -> {v}")
    io["debt_ratio"][k] = v
io["debt_ratio_source"] = {
    "房地产": f"国资委全行业平均（{debt_re.iloc[-1]['日期']:%Y-%m}，{re_debt}%）",
    "建筑业/钢铁/建材/家用电器": "申万三级行业近5年均值（上市公司口径）",
    "其余部门": "演示口径（学弟数据未覆盖，待补）",
}
(APP_DATA / "io_table.json").write_text(json.dumps(io, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"  已写入 io_table.json")

# ============ 2. 宏观月度序列 ============
print("== 2. 生成 macro_monthly.json ==")
series = {}

def add_monthly(name: str, col_kw: str, key: str, exact: bool = True):
    df = read_any(name)
    tcol = df.columns[0]
    for c in df.columns[1:]:
        if (exact and c == col_kw) or (not exact and col_kw in str(c)):
            s = pd.to_numeric(df[c], errors="coerce")
            dates = pd.to_datetime(df[tcol]).dt.strftime("%Y-%m")
            series[key] = {d: (None if pd.isna(v) else round(float(v), 2))
                           for d, v in zip(dates, s)}
            n = sum(v is not None for v in series[key].values())
            print(f"  {key}: {n}期 ({dates.iloc[0]}~{dates.iloc[-1]})" if hasattr(dates, 'iloc') else "")
            return
    print(f"  [WARN] 未找到列: {col_kw} in {name}")

add_monthly("商品房销售额（近5年月度）.xlsx", "中国:商品房销售面积:累计同比(%)", "销售面积同比")
add_monthly("商品房销售额（近5年月度）.xlsx", "中国:商品房销售额:累计同比(%)", "销售额同比")
add_monthly("房地产开发投资完成额（近5年月度）.xlsx", "中国:房地产开发投资完成额:累计同比(%)", "开发投资同比")
add_monthly("房屋新开工面积（近5年月度）.xlsx", "中国:房屋新开工面积:累计同比(%)", "新开工同比")
add_monthly("房屋施工面积（近5年月度）.xlsx", "中国:房屋施工面积:累计同比(%)", "施工同比")
add_monthly("平板玻璃产量（近5年月度）.xlsx", "中国:产量:水泥:累计同比(%)", "水泥产量同比")
add_monthly("平板玻璃产量（近5年月度）.xlsx", "中国:产量:粗钢:累计同比(%)", "粗钢产量同比")
add_monthly("平板玻璃产量（近5年月度）.xlsx", "中国:产量:平板玻璃:累计同比(%)", "玻璃产量同比")
add_monthly("PPI（近5年月度）.xlsx", "中国:PPI:当月同比(%)", "PPI同比")

macro = {
    "metadata": {"source": "Wind/国家统计局（学弟2026-09-30数据包）",
                 "frequency": "月度（累计同比%）", "coverage": "2021-10 ~ 2026-08"},
    "series": series,
}
(APP_DATA / "macro_monthly.json").write_text(json.dumps(macro, ensure_ascii=False), encoding="utf-8")
print(f"  已写入 macro_monthly.json（{len(series)} 个序列）")

# ============ 3. 房地产财务长序列 ============
print("== 3. 生成 industry_finance.json ==")
fin = {
    "metadata": {"source": "Wind（国资委/人行口径），学弟2026-09-30数据包",
                 "note": "全行业平均口径年度序列；现金流动负债比率单位%"},
    "资产负债率_房地产业": {d.strftime("%Y"): round(v, 2) for d, v in zip(
        wind_csv("中国_资产负债率_全行业平均值_房地产业.csv")["日期"],
        wind_csv("中国_资产负债率_全行业平均值_房地产业.csv")["值"])},
    "现金流动负债比率_房地产": {d.strftime("%Y"): round(v, 2) for d, v in zip(
        wind_csv("中国_现金流动负债比率_全行业平均值_房地产企业.csv")["日期"],
        wind_csv("中国_现金流动负债比率_全行业平均值_房地产企业.csv")["值"])},
    "带息负债比率_房地产业": {d.strftime("%Y"): round(v, 2) for d, v in zip(
        wind_csv("中国_带息负债比率_全行业平均值_房地产.csv")["日期"],
        wind_csv("中国_带息负债比率_全行业平均值_房地产.csv")["值"])},
}
(APP_DATA / "industry_finance.json").write_text(json.dumps(fin, ensure_ascii=False), encoding="utf-8")
print(f"  已写入 industry_finance.json")
print("\n全部完成 ✔")
