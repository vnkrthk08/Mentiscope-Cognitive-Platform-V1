import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_endpoint(async_client: AsyncClient):
    """Verifies that GET /api/v1/health returns 200 OK and structured health status."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["HEALTHY", "DEGRADED"]
    assert "version" in data
    assert "environment" in data
    assert data["liveness"] is True
    assert data["readiness"] is True
    assert "components" in data


@pytest.mark.asyncio
async def test_system_llm_status_endpoint(async_client: AsyncClient):
    """Verifies that GET /api/v1/system/llm/status returns 200 OK and LLM diagnostics."""
    response = await async_client.get("/api/v1/system/llm/status")
    assert response.status_code == 200
    data = response.json()
    assert "provider" in data
    assert "selected_model" in data
    assert "llm_mode" in data
    assert "provider_initialized" in data
    assert "api_key_loaded" in data
    assert "connection_status" in data
    assert "last_successful_initialization" in data
    assert "latest_provider_error" in data
