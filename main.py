"""
API Gen Platform — FastAPI Application Entry Point.

Mounts all routes, initializes the database, and serves the frontend.
"""
import sys
import os
from pathlib import Path

# Ensure the project root is on the path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import init_db, SessionLocal
from discovery.knowledge_base import seed_database
from routes.discovery import router as discovery_router
from routes.generator import router as generator_router
from routes.agent import router as agent_router

# ─── Application ─────────────────────────────────────────
app = FastAPI(
    title="🚀 API Gen Platform",
    description=(
        "AI-Powered API Discovery & REST API Generator.\n\n"
        "**Features:**\n"
        "- 🔍 Discover the best APIs for your application idea\n"
        "- 🏆 Ranked by composite score (popularity, docs, reliability, pricing, latency)\n"
        "- 🔬 Analyze Python code and auto-generate REST APIs\n"
        "- 📦 Generate deployment configs (Docker, K8s, AWS, Vercel, Railway)\n"
        "- 🤖 AI Agent Mode for intelligent API recommendation\n"
        "- 💻 CLI tool: `api-gen scan`, `api-gen recommend`, `api-gen deploy`"
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

# ─── Static Files (Frontend) ─────────────────────────────
frontend_dir = Path(__file__).parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


# ─── Root & Health ────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root():
    """Serve the frontend SPA."""
    index_path = frontend_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {
        "name": "API Gen Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
    }


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


# ─── Startup ─────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    """Initialize database and seed API catalog on startup."""
    init_db()
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()


# ─── Entry Point ─────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    from config import HOST, PORT, DEBUG
    uvicorn.run("main:app", host=HOST, port=PORT, reload=DEBUG)
