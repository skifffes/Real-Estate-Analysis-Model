# -*- coding: utf-8 -*-
"""数据反馈_第二轮.md → HTML"""
import markdown
from pathlib import Path

src = Path(r"d:\python\Financial\docs\数据反馈_第二轮.html.md")
body = markdown.markdown(src.read_text(encoding="utf-8"), extensions=["tables", "fenced_code"])

CSS = """
body { font-family: "PingFang SC","Microsoft YaHei",system-ui,sans-serif;
       max-width: 880px; margin: 0 auto; padding: 32px 24px;
       color: #1e293b; background: #f8fafc; line-height: 1.75; }
h1 { color: #1d4ed8; border-bottom: 3px solid #3b82f6; padding-bottom: 10px; }
h2 { color: #1e40af; margin-top: 36px; border-left: 4px solid #3b82f6; padding-left: 12px; }
blockquote { background: #eff6ff; border-left: 4px solid #93c5fd;
             margin: 16px 0; padding: 10px 16px; border-radius: 0 8px 8px 0; color: #3730a3; }
table { border-collapse: collapse; width: 100%; margin: 16px 0; background: #fff; }
th, td { border: 1px solid #cbd5e1; padding: 8px 12px; text-align: left; font-size: 14px; }
th { background: #dbeafe; color: #1e3a8a; }
tr:nth-child(even) td { background: #f1f5f9; }
code { background: #e2e8f0; padding: 2px 6px; border-radius: 4px; font-size: 13px; color: #be185d; }
hr { border: none; border-top: 1px solid #cbd5e1; margin: 28px 0; }
li { margin: 4px 0; }
"""

html = ("<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
        "<title>数据提交反馈（第二轮）</title><style>" + CSS + "</style></head><body>"
        + body + "</body></html>")

dst = src.with_suffix(".html")
dst.write_text(html, encoding="utf-8")
print(f"已生成: {dst} ({len(html)//1024}KB)")
