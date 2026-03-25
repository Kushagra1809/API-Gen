"""
Vercel Serverless Function Entry Point for FastAPI.
"""
import sys
from pathlib import Path

# Add the project root to the path so imports work correctly
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from contextlib import asynccontextmanager
import os

# Set a writable tmp directory for SQLite on Vercel
os.environ.setdefault("API_GEN_DB_PATH", "/tmp/api_platform.db")

from database import init_db, SessionLocal
from discovery.knowledge_base import seed_database
from routes.discovery import router as discovery_router
from routes.generator import router as generator_router
from routes.agent import router as agent_router

# ─── Lifespan ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and seed API catalog on startup."""
    init_db()
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    yield

# ─── Application ─────────────────────────────────────────
app = FastAPI(
    title="API Gen Platform",
    lifespan=lifespan,
    description=(
        "AI-Powered API Discovery & REST API Generator.\n\n"
        "**Features:**\n"
        "- Discover the best APIs for your application idea\n"
        "- Ranked by composite score (popularity, docs, reliability, pricing, latency)\n"
        "- Analyze Python code and auto-generate REST APIs\n"
        "- Generate deployment configs (Docker, K8s, AWS, Vercel, Railway, Render)\n"
        "- AI Agent Mode for intelligent API recommendation\n"
        "- CLI tool: `api-gen scan`, `api-gen recommend`, `api-gen deploy`"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ─── CORS ─────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routes ───────────────────────────────────────────────
app.include_router(discovery_router)
app.include_router(generator_router)
app.include_router(agent_router)

# ─── Root & Health ────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root():
    """Serve the frontend SPA or return API info."""
    frontend_dir = project_root / "frontend"
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return JSONResponse({
        "name": "API Gen Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
    })


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


# Export handler for Vercel
handler = app
