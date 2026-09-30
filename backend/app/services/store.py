"""SQLite 持久化：reports / uploads 落库，服务重启后恢复（ROADMAP 2.1）"""
import json
import sqlite3
from pathlib import Path

from ..config import DATA_DIR

DB_PATH = DATA_DIR / "app.db"


def _conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    with _conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS reports (
            report_id TEXT PRIMARY KEY, question TEXT, risk_level TEXT,
            risk_score REAL, created_at TEXT, data TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS uploads (
            file_id TEXT PRIMARY KEY, filename TEXT, data TEXT NOT NULL)""")
    return f"sqlite @ {DB_PATH.name}"


# ---------- reports ----------
def save_report(report: dict):
    with _conn() as c:
        c.execute("INSERT OR REPLACE INTO reports VALUES (?,?,?,?,?,?)",
                  (report["report_id"], report.get("question", ""),
                   report.get("risk_level"), report.get("risk_score"),
                   report.get("created_at"), json.dumps(report, ensure_ascii=False)))


def load_reports() -> dict:
    with _conn() as c:
        rows = c.execute("SELECT data FROM reports ORDER BY created_at").fetchall()
    return {r["report_id"]: r for r in (json.loads(x[0]) for x in rows)}


def delete_report(report_id: str):
    with _conn() as c:
        c.execute("DELETE FROM reports WHERE report_id=?", (report_id,))


def clear_reports():
    with _conn() as c:
        c.execute("DELETE FROM reports")


# ---------- uploads ----------
def save_upload(fid: str, filename: str, summary: dict):
    with _conn() as c:
        c.execute("INSERT OR REPLACE INTO uploads VALUES (?,?,?)",
                  (fid, filename, json.dumps(summary, ensure_ascii=False)))


def load_uploads() -> dict:
    with _conn() as c:
        rows = c.execute("SELECT file_id, data FROM uploads").fetchall()
    return {fid: json.loads(d) for fid, d in rows}
