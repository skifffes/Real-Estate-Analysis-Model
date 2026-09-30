# -*- coding: utf-8 -*-
"""全量检查学弟提供的32个数据文件：结构/时间范围/有效性"""
import pandas as pd
from pathlib import Path

BASE = Path(r"d:\python\Financial\项目竞赛资料\传导机制部分所需数据2026年9月30日")
DOC = Path(r"d:\python\Financial\项目竞赛资料\传导机制部分分析2026年9月30日")

def read_any(p: Path):
    if p.suffix == ".csv":
        for enc in ("utf-8-sig", "gbk", "gb18030"):
            try:
                return pd.read_csv(p, encoding=enc)
            except UnicodeDecodeError:
                continue
        raise UnicodeDecodeError
    return pd.read_excel(p)

print("========== 数据文件（33个） ==========")
for p in sorted(BASE.iterdir()):
    if not p.is_file():
        continue
    try:
        df = read_any(p)
        tcol = df.columns[0]
        tmin = df[tcol].min()
        tmax = df[tcol].max()
        nan_pct = df.isna().mean().mean() * 100
        print(f"[OK] {p.name}")
        print(f"     {df.shape[0]}行×{df.shape[1]}列 | 时间 {tmin} ~ {tmax} | 缺失率 {nan_pct:.0f}%")
        print(f"     列: {[str(c)[:36] for c in df.columns]}")
    except Exception as e:
        print(f"[FAIL] {p.name}: {type(e).__name__}: {e}")

print()
print("========== 分析文档（3个） ==========")
for p in sorted(DOC.iterdir()):
    if p.is_file():
        print(f"{p.name} ({p.stat().st_size//1024}KB)")
