# -*- coding: utf-8 -*-
"""生成 CRLF 测试 bat 并运行验证解析"""
import subprocess
from pathlib import Path

bat = "\r\n".join([
    "@echo off",
    "chcp 65001 >nul",
    "cd /d \"%~dp0\"",
    "echo LINE-OK-1",
    "where python >nul 2>nul",
    "if errorlevel 1 (",
    "    echo NO-PYTHON",
    ") else (",
    "    echo PYTHON-OK",
    ")",
    "if not exist \"backend\\app\\data\\io_table.json\" (",
    "    echo NO-BACKEND",
    ") else (",
    "    echo BACKEND-OK",
    ")",
    "echo DONE",
    "",
])
p = Path(r"d:\python\Financial\_test.bat")
p.write_bytes(bat.encode("utf-8"))

r = subprocess.run(["cmd", "/c", str(p)], capture_output=True, text=True, encoding="utf-8", errors="replace")
print("STDOUT:", r.stdout)
print("STDERR:", r.stderr)
p.unlink()
