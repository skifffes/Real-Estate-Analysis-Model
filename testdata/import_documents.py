# -*- coding: utf-8 -*-
"""批量导入资料 → 知识库文档
PDF / DOCX / DOC / XLS(X) → backend/app/knowledge/documents/*.md
转换规则：
- PDF/DOCX: 提取正文，清洗后写入 md（扫描版无文本层的 PDF 会跳过并记录）
- XLS/XLSX: 投入产出表等数据文件 → 转为带表头的 markdown 表格文本
"""
import re
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DOCS = BASE / "backend" / "app" / "knowledge" / "documents"
DOCS.mkdir(parents=True, exist_ok=True)

SRC_DIRS = [
    BASE / "项目竞赛资料" / "文献资料",
    BASE / "项目竞赛资料" / "北京市投入产出表",
    BASE / "项目竞赛资料" / "北京市国民经济统计报告",
    BASE,  # 根目录的两篇论文 PDF
]

ok, failed, skipped = [], [], []
IMPORTED_TAG = "<!-- imported -->"


def clean_text(text: str) -> str:
    """清洗 PDF 提取文本：去页码、合并断行、压空行、剔除非法代理字符"""
    text = text.encode("utf-8", errors="ignore").decode("utf-8")  # 去 surrogates 等非法字符
    text = re.sub(r"\n\s*\d+\s*\n", "\n", text)            # 独立页码行
    text = re.sub(r"-\n(\w)", r"\1", text)                  # 英文断词
    text = re.sub(r"[ \t]+", " ", text)                     # 压空白
    text = re.sub(r"\n{3,}", "\n\n", text)                  # 压空行
    return text.strip()


def pdf_to_md(src: Path) -> str | None:
    from pypdf import PdfReader
    try:
        reader = PdfReader(str(src))
        parts = []
        for page in reader.pages:
            t = page.extract_text() or ""
            if t.strip():
                parts.append(t)
        text = clean_text("\n".join(parts))
        return text if len(text) > 500 else None  # 太短视为扫描版/无文本层
    except Exception as e:
        print(f"  [PDF失败] {src.name}: {e}")
        return None


def docx_to_md(src: Path) -> str | None:
    import docx
    try:
        d = docx.Document(str(src))
        parts = [p.text for p in d.paragraphs if p.text.strip()]
        for tb in d.tables:  # 表格转文本
            for row in tb.rows:
                parts.append(" | ".join(c.text.strip() for c in row.cells))
        text = clean_text("\n".join(parts))
        return text if len(text) > 200 else None
    except Exception as e:
        print(f"  [DOCX失败] {src.name}: {e}")
        return None


def excel_to_md(src: Path) -> str | None:
    """数据表 → markdown 表格（前若干行有效数据）"""
    import pandas as pd
    try:
        sheets = pd.read_excel(str(src), sheet_name=None, header=None)
        parts = [f"# 数据表：{src.stem}", f"\n来源文件：{src.name}\n"]
        for name, df in sheets.items():
            df = df.dropna(how="all").dropna(axis=1, how="all")
            if df.empty:
                continue
            parts.append(f"\n## 工作表：{name}\n")
            head = df.head(40).fillna("")  # 前40行足够知识库检索
            for _, row in head.iterrows():
                cells = [str(v).strip() for v in row.tolist()]
                if any(cells):
                    parts.append("| " + " | ".join(cells) + " |")
        text = "\n".join(parts)
        return text if len(text) > 200 else None
    except Exception as e:
        print(f"  [Excel失败] {src.name}: {e}")
        return None


def target_name(src: Path, idx: int) -> Path:
    stem = re.sub(r"[\\/:*?\"<>|（）()【】\s]+", "_", src.stem)[:40]
    return DOCS / f"imported_{idx:02d}_{stem}.md"


def main():
    idx = 0
    files = []
    for d in SRC_DIRS:
        if not d.exists():
            continue
        for f in sorted(d.iterdir()):
            if f.is_file() and f.suffix.lower() in (".pdf", ".docx", ".doc", ".xls", ".xlsx"):
                # 根目录只收论文 PDF，跳过计划书
                if d == BASE and "计划书" in f.name:
                    continue
                files.append(f)

    print(f"发现 {len(files)} 个待导入文件")
    for f in files:
        idx += 1
        dst = target_name(f, idx)
        if dst.exists() and IMPORTED_TAG in dst.read_text(encoding="utf-8")[:100]:
            print(f"  [已导入] {f.name}")
            continue
        suffix = f.suffix.lower()
        if suffix == ".pdf":
            text = pdf_to_md(f)
        elif suffix in (".docx", ".doc"):
            text = docx_to_md(f)
        else:
            text = excel_to_md(f)
        if text is None:
            failed.append(f.name)
            continue
        header = (f"{IMPORTED_TAG}\n# {f.stem}\n\n"
                  f"> 类别：背景资料 | 来源：{f.parent.name}/{f.name}\n\n")
        dst.write_text(header + text, encoding="utf-8")
        ok.append(f.name)
        print(f"  [OK] {f.name} -> {dst.name} ({len(text)//1000}k字)")

    print(f"\n完成：成功 {len(ok)} | 失败 {len(failed)} | 目录: {DOCS}")
    if failed:
        print("失败清单（多为扫描版无文本层，需OCR，暂跳过）：")
        for n in failed:
            print("  -", n)


if __name__ == "__main__":
    main()
