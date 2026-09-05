from fastapi import APIRouter
from pydantic import BaseModel
from app.core.config import settings

router = APIRouter()


class HealthCheckResponse(BaseModel):
    status: str
    project_name: str
    version: str
    environment: str
    adaptive_followup_enabled: bool


@router.get("/health", response_model=HealthCheckResponse, summary="System Health & Bootstrap Status")
async def check_health():
    """Health check endpoint confirming FastAPI backend operational status."""
    return HealthCheckResponse(
        status="healthy",
        project_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENV,
        adaptive_followup_enabled=settings.ENABLE_ADAPTIVE_FOLLOWUP,
    )
