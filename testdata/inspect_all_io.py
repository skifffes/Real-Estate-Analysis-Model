# -*- coding: utf-8 -*-
"""检查各年份北京投入产出表的结构（部门数/表头行/单位行）"""
import pandas as pd
from pathlib import Path

BASE = Path(r"d:\python\Financial\项目竞赛资料\北京市投入产出表")
for f in sorted(BASE.glob("*.xls*")):
    try:
        xl = pd.ExcelFile(f)
        info = [f"sheets={xl.sheet_names}"]
        # 取第一个流量表 sheet
        for sn in xl.sheet_names:
            if "流量" in sn or len(xl.sheet_names) == 1:
                df = pd.read_excel(f, sheet_name=sn, header=None)
                # 找部门名行（含'农林牧渔'或'投入'表头）
                sector_row, n_sector = None, 0
                for i in range(min(15, len(df))):
                    row = df.iloc[i].tolist()
                    cnt = sum(1 for v in row if pd.notna(v) and ("产品" in str(v) or "服务" in str(v) or str(v).strip() in ("农林牧渔",)))
                    if cnt >= 5:
                        sector_row = i
                        names = [str(v).strip() for v in row if pd.notna(v) and len(str(v).strip()) > 1]
                        # 数一下列方向部门数
                        n_sector = sum(1 for v in row if pd.notna(v) and str(v).strip() not in ("产出", "代码", "中间使用", "中间使用合计"))
                        break
                info.append(f"sheet[{sn}] shape={df.shape} 部门名行≈{sector_row} 部门数≈{n_sector}")
                break
        print(f"{f.name}: " + " | ".join(info))
    except Exception as e:
        print(f"{f.name}: 读取失败 {type(e).__name__}: {e}")
