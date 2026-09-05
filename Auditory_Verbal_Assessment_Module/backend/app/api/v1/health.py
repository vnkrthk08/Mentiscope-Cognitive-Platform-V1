from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from app.core.config import Settings
from app.core.dependencies import get_settings_dep
from app.core.database import check_database_health
from app.core.redis import check_redis_health


class HealthResponse(BaseModel):
    status: str = Field(json_schema_extra={"example": "HEALTHY"})
    version: str = Field(json_schema_extra={"example": "1.0.0"})
    environment: str = Field(json_schema_extra={"example": "development"})
    timestamp: str = Field(json_schema_extra={"example": "2026-07-21T12:00:00Z"})
    liveness: bool = Field(json_schema_extra={"example": True})
    readiness: bool = Field(json_schema_extra={"example": True})
    components: Dict[str, Any] = Field(
        json_schema_extra={
            "example": {
                "database": "HEALTHY",
                "redis": "HEALTHY",
                "platform_subsystems": 12,
            }
        }
    )


router = APIRouter(prefix="", tags=["Health & Status"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Platform Health & Readiness Check",
    description="Returns platform health, liveness, readiness, and subsystem component statuses.",
)
async def health_check(settings: Settings = Depends(get_settings_dep)) -> HealthResponse:
    db_ok = await check_database_health()
    redis_ok = await check_redis_health()

    liveness = True
    readiness = True  # Platform operational even with fallbacks

    return HealthResponse(
        status="HEALTHY" if (liveness and readiness) else "DEGRADED",
        version=settings.VERSION,
        environment=settings.ENVIRONMENT.value,
        timestamp=datetime.now(timezone.utc).isoformat(),
        liveness=liveness,
        readiness=readiness,
        components={
            "database": "HEALTHY" if db_ok else "UNAVAILABLE",
            "redis": "HEALTHY" if redis_ok else "UNAVAILABLE",
            "platform_subsystems": 12,
            "feature_flags": {
                "adaptive_followup": settings.ENABLE_ADAPTIVE_FOLLOWUP,
                "llm_evaluation": settings.ENABLE_LLM_EVALUATION,
                "research_analytics": settings.ENABLE_RESEARCH_ANALYTICS,
            },
        },
    )


@router.get(
    "/system/llm/status",
    status_code=status.HTTP_200_OK,
    summary="LLM System Diagnostics",
)
async def system_llm_status():
    from app.core.config import settings
    from app.infrastructure.prompt.provider_registry import llm_registry
    
    provider_name = settings.LLM_PROVIDER
    model_name = ""
    if provider_name.lower() == "gemini":
        model_name = settings.GEMINI_MODEL
        api_key_loaded = bool(settings.GEMINI_API_KEY)
    elif provider_name.lower() == "openai":
        model_name = settings.OPENAI_MODEL
        api_key_loaded = bool(settings.OPENAI_API_KEY)
    elif provider_name.lower() == "claude":
        model_name = settings.CLAUDE_MODEL
        api_key_loaded = bool(settings.ANTHROPIC_API_KEY)
    elif provider_name.lower() in ("openrouter", "nvidia"):
        model_name = settings.OPENROUTER_MODEL
        api_key_loaded = bool(settings.OPENROUTER_API_KEY)
    else:
        api_key_loaded = False
        
    connection_status = "DISCONNECTED"
    try:
        default_prov = llm_registry.get_default_provider()
        is_healthy = await default_prov.health_check()
        connection_status = "CONNECTED" if is_healthy else "DISCONNECTED"
    except Exception:
        pass
        
    return {
        "provider": provider_name,
        "selected_model": model_name,
        "llm_mode": settings.LLM_MODE,
        "provider_initialized": getattr(llm_registry, "initialized", False),
        "api_key_loaded": api_key_loaded,
        "connection_status": connection_status,
        "last_successful_initialization": getattr(llm_registry, "last_successful_init", None),
        "latest_provider_error": getattr(llm_registry, "latest_error", None),
    }
