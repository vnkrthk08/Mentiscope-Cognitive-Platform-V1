"""
==========================================================
MentiScope Gq Assessment Engine
Main FastAPI Application
==========================================================
"""

from contextlib import asynccontextmanager
from app.api.answer import router as answer_router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.start import router as start_router
from app.core.config import settings
from app.api.finish import router as finish_router
from app.api.result import router as result_router

# ==========================================================
# Lifespan Events
# ==========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and Shutdown Events.
    Database initialization and other startup
    services will be added here later.
    """
    
    from app.database.base import Base
    from app.database.database import engine
    
    Base.metadata.create_all(bind=engine)

    print("Starting MentiScope Gq Assessment Engine...")

    yield

    print("Shutting down MentiScope Gq Assessment Engine...")


# ==========================================================
# FastAPI Application
# ==========================================================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## MentiScope – Quantitative Ability (Gq)

AI-powered adaptive cognitive assessment engine.

### Features

- Adaptive Question Routing
- Dynamic Question Generation
- Difficulty Calibration
- Item Exposure Control
- Event Logging
- Behavioral Analytics
- Recommendation Engine
- SDK Compatible
- REST API
- OpenAPI Documentation

Developed as part of the MentiScope Cognitive Assessment Platform.
""",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ==========================================================
# Middleware
# ==========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# Root Endpoint
# ==========================================================

@app.get(
    "/",
    tags=["System"],
    summary="Service Information",
)
async def root():
    """
    Root endpoint.

    Returns information about the running service.
    """

    return {
        "service": settings.APP_NAME,
        "module": settings.MODULE_NAME,
        "module_id": settings.MODULE_ID,
        "construct": settings.CONSTRUCT,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "status": "running",
    }


# ==========================================================
# Health Check
# ==========================================================

@app.get(
    "/health",
    tags=["System"],
    summary="Health Check",
)
async def health():
    """
    Health endpoint for deployment monitoring.
    """

    return {
        "status": "healthy",
        "engine": "ready",
        "database": "pending",
        "api": "online",
        "version": settings.APP_VERSION,
    }


# ==========================================================
# Module Information
# ==========================================================

@app.get(
    "/module",
    tags=["System"],
    summary="Module Information",
)
async def module():
    """
    Returns metadata about this assessment module.
    """

    return {
        "module_id": settings.MODULE_ID,
        "module_name": settings.MODULE_NAME,
        "construct": settings.CONSTRUCT,
        "difficulty_levels": settings.MAX_LEVEL,
        "question_bank": settings.QUESTION_BANK_SIZE,
        "adaptive": True,
        "version": settings.APP_VERSION,
    }
print(settings.DATABASE_URL)
app.include_router(answer_router)
app.include_router(start_router)
app.include_router(finish_router)
app.include_router(result_router)
# ==========================================================
# Future API Routers
# ==========================================================

# from app.api.start import router as start_router
# from app.api.answer import router as answer_router
# from app.api.finish import router as finish_router
# from app.api.result import router as result_router

# app.include_router(start_router, prefix=settings.API_PREFIX)
# app.include_router(answer_router, prefix=settings.API_PREFIX)
# app.include_router(finish_router, prefix=settings.API_PREFIX)
# app.include_router(result_router, prefix=settings.API_PREFIX)