"""
ASAT – FastAPI Main Entry Point

Translated from: backend/server.js
Same CORS setup, same JSON parsing, same route mounting.
Added: Starlette SessionMiddleware for session-based auth (replacing express-session).
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import JSONResponse
import sys

from app.config import settings
from app.database import init_db, shutdown_db
from app.routers import auth, students, sessions, reports, assessment

# ── Logging Setup ──
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("asat.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events: translated from db.js initDB() call on startup."""
    logger.info("Starting ASAT API Server...")
    await init_db()
    yield
    logger.info("Shutting down ASAT API Server...")
    await shutdown_db()


app = FastAPI(
    title="ASAT – Adaptive Shape Attention Task API",
    description="MentiScope Module + Legacy Frontend APIs",
    version="2.0.0",
    lifespan=lifespan,
)

# ── Middleware ──
# 1. CORS — Same as express cors() setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Sessions — Same as express-session setup
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.app_secret_key,
    session_cookie="asat_session",
    max_age=86400,  # 24 hours
    same_site="lax",
    https_only=False,  # Set True in prod with HTTPS
)


# ── Global Exception Handler ──
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error. Please try again later."},
    )


# ── Mount Routers ──
# These map exactly to the app.use("/api/...", ...) calls in server.js
app.include_router(auth.router)
app.include_router(students.router)
app.include_router(sessions.router)
app.include_router(reports.router)

# New MentiScope standard endpoints (POST /api/start, POST /api/answer, etc.)
app.include_router(assessment.router)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "module": settings.module_id}
