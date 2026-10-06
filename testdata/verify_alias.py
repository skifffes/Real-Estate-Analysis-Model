# -*- coding: utf-8 -*-
"""验证行业别名表 + 未识别行业拒绝量化"""
import sys
sys.path.insert(0, r"d:\python\Financial\backend")
from app.agent.core import _supply_sector

# 别名映射
cases = [
    ("水泥减产15%会有什么影响？", "建材"),     # 反馈点名的场景
    ("玻璃供给收缩10%", "建材"),
    ("钢材减产10%", "钢铁"),
    ("家电库存限产10%", "家用电器"),
    ("电力限产20%", "电力热力"),
    ("工程机械供给减少10%", "机械设备"),
    ("物流供给下降10%", "交通运输"),
]
print("== 别名表映射 ==")
ok = True
for q, exp in cases:
    got = _supply_sector(q)
    o = got == exp
    ok = ok and o
    print(f"{'OK' if o else 'FAIL'} {q[:22]} -> {got}（期望 {exp}）")

# 无法映射 → 拒绝（不猜测钢铁）
r = _supply_sector("光伏组件减产15%会有什么影响？")
print(f"\n无法映射（光伏组件）: '{r}' -> 拒绝量化 {'OK' if r == '' else 'FAIL（不应默认钢铁）'}")
