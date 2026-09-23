"""房地产产业链风险分析智能体 —— FastAPI 入口"""
import json
import uuid
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel

from .config import DATA_DIR, UPLOAD_DIR
from .knowledge import rag
from .agent.core import RiskAgent
from .agent.tools import execute_tool
from .models import input_output as io
from .services import upload as upload_svc
from .services import report as report_svc

STATE = {"reports": {}, "uploads": {}, "dashboard": {}}
AGENT = RiskAgent()


def _default_dashboard() -> dict:
    macro = json.loads((DATA_DIR / "macro_history.json").read_text(encoding="utf-8"))
    return {
        "risk_score": 0, "risk_level": "-",
        "industry_impact": [], "industry_scores": [], "key_indicators": [],
        "supply_chain": io.supply_chain_graph(),
        "historical_comparison": macro,
        "updated_at": None,
    }


def _refresh_dashboard(report: dict):
    # 仅当报告含量化分析结果时才刷新仪表盘，避免定性问题清空已有数据
    if not report.get("affected_industries"):
        return
    d = STATE["dashboard"]
    d["risk_score"] = report.get("risk_score", 0)
    d["risk_level"] = report.get("risk_level", "-")
    d["industry_impact"] = [
        {"name": r["industry"], "value": r["impact_pct"]} for r in report.get("affected_industries", [])
    ]
    d["industry_scores"] = report.get("industry_scores", [])
    d["key_indicators"] = report.get("key_indicators", [])
    impact = report.get("impact")
    d["supply_chain"] = io.supply_chain_graph(impact)
    d["similar_cases"] = report.get("similar_cases", [])
    d["updated_at"] = report.get("created_at")


@asynccontextmanager
async def lifespan(app: FastAPI):
    kb_status = rag.build_knowledge_base()
    STATE["dashboard"] = _default_dashboard()
    print(f"[KB] 知识库就绪: {kb_status}  |  Agent 模式: {AGENT.mode}")
    yield


app = FastAPI(title="房地产产业链风险分析智能体", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


class ChatRequest(BaseModel):
    question: str


# ---------- Module 1/3/4: Agent 问答 ----------
@app.post("/api/chat")
def chat(req: ChatRequest):
    if not req.question.strip():
        raise HTTPException(400, "问题不能为空")
    report, trace = AGENT.run(req.question, ctx={
        "uploads": STATE["uploads"],
        "dashboard": STATE["dashboard"],
    })
    report["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    report["tool_trace"] = trace
    report["agent_mode"] = AGENT.mode
    report["report_id"] = str(uuid.uuid4())[:8]
    STATE["reports"][report["report_id"]] = report
    report_svc.save_report(report)
    _refresh_dashboard(report)
    return report


# ---------- 数据上传 ----------
@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename.lower().endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(400, "仅支持 CSV / Excel 文件")
    fid = str(uuid.uuid4())[:8]
    path = UPLOAD_DIR / f"{fid}_{file.filename}"
    path.write_bytes(await file.read())
    try:
        summary = upload_svc.analyze_file(str(path), file.filename)
    except Exception as e:
        raise HTTPException(422, f"文件解析失败: {e}")
    summary["file_id"] = fid
    STATE["uploads"][fid] = summary
    return summary


# ---------- Dashboard ----------
@app.get("/api/dashboard")
def dashboard():
    return STATE["dashboard"]


# ---------- 报告 ----------
@app.get("/api/reports")
def list_reports():
    items = [{"report_id": r["report_id"], "question": r.get("question", ""),
              "risk_level": r.get("risk_level"), "risk_score": r.get("risk_score"),
              "created_at": r.get("created_at")}
             for r in reversed(list(STATE["reports"].values()))]
    return {"items": items, "reports_dir": "backend/reports/"}


@app.get("/api/report/{rid}")
def get_report(rid: str):
    if rid not in STATE["reports"]:
        raise HTTPException(404, "报告不存在（服务重启后内存态清空，Markdown 文件仍在 backend/reports/）")
    return STATE["reports"][rid]


@app.get("/api/report/{rid}/download")
def download_report(rid: str):
    from .config import REPORTS_DIR
    path = REPORTS_DIR / f"{rid}.md"
    if not path.exists():
        raise HTTPException(404, "报告文件不存在")
    return FileResponse(path, media_type="text/markdown",
                        filename=f"房地产产业链风险分析报告_{rid}.md")


# ---------- 知识库演示接口 ----------
@app.get("/api/kb/search")
def kb_search(q: str, top_k: int = 4):
    return {"results": rag.search(q, top_k)}


@app.get("/api/kb/status")
def kb_status():
    return {"status": "ok"}


@app.get("/api/health")
def health():
    return {"status": "ok", "agent_mode": AGENT.mode}
