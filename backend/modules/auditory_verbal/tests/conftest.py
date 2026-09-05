import os
import sys
import pytest
from httpx import AsyncClient, ASGITransport

# Set environment overrides for tests BEFORE app import
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["ENVIRONMENT"] = "testing"

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import app as fastapi_app  # noqa: E402
from app.infrastructure.persistence.database.base import Base
from app.infrastructure.persistence.database.engine import engine
from app.infrastructure.platform_integration import PlatformIntegrationManager
from app.application.identity.services.auth_service import AuthService

# Explicitly import all ORM models to populate Base.metadata before create_all
import app.infrastructure.persistence.models.orm_models
import app.infrastructure.identity.orm_models
import app.infrastructure.media.orm_models
import app.infrastructure.speech.orm_models
import app.infrastructure.prompt.orm_models
import app.infrastructure.behavior.orm_models
import app.infrastructure.construct.orm_models
import app.infrastructure.assessment.orm_models
import app.infrastructure.research.orm_models  # PVCSF tables
import app.infrastructure.analytics.orm_models  # RAIP tables
import app.infrastructure.governance.orm_models  # MGEP tables
import app.infrastructure.actp.orm_models  # ACTP tables
import app.infrastructure.operations.orm_models  # POSRP tables


@pytest.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Initializes in-memory database schema and platform manager for all integration tests."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Manually initialize platform manager to guarantee app.state has it during client calls
    platform_mgr = PlatformIntegrationManager()
    await platform_mgr.initialize_platform(env="testing")
    fastapi_app.state.platform_manager = platform_mgr

    # Seed baseline roles and permissions
    await AuthService.seed_roles_and_permissions()

    yield

    await platform_mgr.shutdown_platform(reason="TESTS_COMPLETE")
    await engine.dispose()


@pytest.fixture
async def async_client():
    """Fixture providing an async HTTP client for FastAPI integration testing."""
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
