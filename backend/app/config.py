"""全局配置"""
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

# LLM（OpenAI 兼容协议，默认智谱 GLM）
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://open.bigmodel.cn/api/paas/v4/")
LLM_MODEL = os.getenv("LLM_MODEL", "glm-4.5")

APP_DIR = Path(__file__).resolve().parent
DATA_DIR = APP_DIR / "data"
KB_DOCS_DIR = APP_DIR / "knowledge" / "documents"
KB_STORE_DIR = APP_DIR / "knowledge" / "kb_store"
KB_CHUNKS_FILE = KB_STORE_DIR / "chunks.json"
UPLOAD_DIR = BASE_DIR / "uploads"
REPORTS_DIR = BASE_DIR / "reports"

for d in (UPLOAD_DIR, REPORTS_DIR, KB_STORE_DIR):
    d.mkdir(parents=True, exist_ok=True)
