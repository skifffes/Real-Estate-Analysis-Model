# -*- coding: utf-8 -*-
"""检查素材文档中的案例内容"""
from pathlib import Path

files = list(Path(r"d:\python\Financial\backend\app\knowledge\documents").glob("imported_64*"))
print("匹配文件:", files)
t = files[0].read_text(encoding="utf-8")
print("总长度:", len(t), "字符\n")

for kw in ["案例", "深圳", "郑州", "温州", "燕郊", "恒大", "日本", "美国", "海南"]:
    cnt = t.count(kw)
    i = t.find(kw)
    print(f"{kw}: 出现{cnt}次, 首次位置 {'有' if i >= 0 else '无'}")

print("\n--- 第一个'案例'附近预览 ---")
i = t.find("案例")
if i >= 0:
    print(t[max(0, i - 100):i + 700])
