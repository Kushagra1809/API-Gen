"""
Vercel Serverless Function Entry Point for FastAPI.
"""
import sys
import os
from pathlib import Path

# Add the project root to the path so imports work correctly
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set environment variable to indicate we're running on Vercel
os.environ["VERCEL"] = "1"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# ─── Application ─────────────────────────────────────────
app = FastAPI(
    title="API Gen Platform",
    description=(
        "AI-Powered API Discovery & REST API Generator.\n\n"
        "**Features:**\n"
        "- Discover the best APIs for your application idea\n"
        "- Ranked by composite score (popularity, docs, reliability, pricing, latency)\n"
        "- Analyze Python code and auto-generate REST APIs\n"
        "- Generate deployment configs (Docker, K8s, AWS, Vercel, Railway, Render)\n"
        "- AI Agent Mode for intelligent API recommendation"
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

# ─── Lazy DB Init ─────────────────────────────────────────
_db_initialized = False

def ensure_db():
    """Lazy database initialization."""
    global _db_initialized
    if not _db_initialized:
        from database import init_db, SessionLocal
        from discovery.knowledge_base import seed_database
        init_db()
        db = SessionLocal()
        try:
            seed_database(db)
        finally:
            db.close()
        _db_initialized = True

# ─── Routes ───────────────────────────────────────────────
from routes.discovery import router as discovery_router
from routes.generator import router as generator_router
from routes.agent import router as agent_router

app.include_router(discovery_router)
app.include_router(generator_router)
app.include_router(agent_router)

# ─── Root & Health ────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root():
    """Return API info."""
    return JSONResponse({
        "name": "API Gen Platform",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running",
        "endpoints": {
            "discover": "/api/discover",
            "apis": "/api/apis",
            "categories": "/api/categories",
            "generate": "/api/generate",
            "agent": "/api/agent",
        }
    })


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/init", tags=["System"])
async def init_database():
    """Initialize database endpoint."""
    try:
        ensure_db()
        return {"status": "initialized"}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ─── Middleware to ensure DB on first request ─────────────
@app.middleware("http")
async def db_init_middleware(request, call_next):
    """Ensure database is initialized before handling requests."""
    if request.url.path.startswith("/api/"):
        try:
            ensure_db()
        except Exception as e:
            return JSONResponse(
                {"error": f"Database initialization failed: {str(e)}"},
                status_code=500
            )
    return await call_next(request)


# Export handler for Vercel
handler = app
