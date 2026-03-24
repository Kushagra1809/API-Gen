"""
Central configuration for the AI API Platform.
"""
import os
from pathlib import Path

# ─── Paths ───────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "api_platform.db"
GENERATED_DIR = BASE_DIR / "generated_projects"
TEMPLATES_DIR = BASE_DIR / "generator" / "templates"

# ─── Database ────────────────────────────────────────────
DATABASE_URL = f"sqlite:///{DB_PATH}"

# ─── Server ──────────────────────────────────────────────
HOST = os.getenv("API_GEN_HOST", "0.0.0.0")
PORT = int(os.getenv("API_GEN_PORT", "8000"))
DEBUG = os.getenv("API_GEN_DEBUG", "true").lower() == "true"

# ─── AI / LLM (optional – system works without it) ──────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4")

# ─── API Scoring Weights ────────────────────────────────
SCORING_WEIGHTS = {
    "popularity":     0.30,
    "documentation":  0.20,
    "reliability":    0.20,
    "pricing":        0.15,
    "latency":        0.15,
}

# ─── Verification ───────────────────────────────────────
HEALTH_CHECK_TIMEOUT = 10          # seconds
MAX_CONCURRENT_CHECKS = 20

# ─── Deployment Defaults ────────────────────────────────
DEFAULT_PYTHON_VERSION = "3.11"
DEFAULT_PORT = 8000

# Ensure directories exist
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
GENERATED_DIR.mkdir(parents=True, exist_ok=True)
