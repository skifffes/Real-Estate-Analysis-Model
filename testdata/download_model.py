# -*- coding: utf-8 -*-
"""走系统代理下载 Chroma MiniLM 语义模型（约80MB），显示进度"""
import pathlib
import sys
import time
import urllib.request

URL = "https://chroma-onnx-models.s3.amazonaws.com/all-MiniLM-L6-v2/onnx.tar.gz"
DEST = pathlib.Path.home() / ".cache" / "chroma" / "onnx_models" / "all-MiniLM-L6-v2" / "onnx.tar.gz"
DEST.parent.mkdir(parents=True, exist_ok=True)

t0 = time.time()
urllib.request.urlretrieve(URL, DEST)
dt = time.time() - t0
size = DEST.stat().st_size / 1024 / 1024
print(f"OK: {size:.1f} MB in {dt:.1f}s = {size/dt:.2f} MB/s -> {DEST}")
