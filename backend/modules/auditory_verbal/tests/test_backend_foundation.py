import pytest
from app.core.config import settings
from app.core.security import SecurityUtils
from app.core.database import check_database_health
from app.core.redis import check_redis_health
from app.core.logging import setup_logging
from app.core.dependencies import get_settings_dep, get_correlation_id


def test_configuration_loading():
    assert settings.PROJECT_NAME is not None
    assert settings.VERSION == "1.0.0"
    assert settings.ENVIRONMENT is not None
    assert settings.async_database_url is not None
    assert settings.active_redis_url is not None


def test_logging_setup():
    setup_logging()
    from app.core.logging import logger

    assert logger is not None


def test_security_utilities():
    password = "SecretPassword123"
    hashed = SecurityUtils.hash_password(password)
    assert hashed != password
    assert SecurityUtils.verify_password(password, hashed) is True
    assert SecurityUtils.verify_password("WrongPassword", hashed) is False

    token = SecurityUtils.create_access_token(subject="CAND-01", claims={"role": "candidate"})
    assert token is not None
    decoded = SecurityUtils.decode_access_token(token)
    assert decoded["sub"] == "CAND-01"
    assert decoded["role"] == "candidate"


@pytest.mark.asyncio
async def test_database_and_redis_health_checks():
    db_health = await check_database_health()
    # Should safely return boolean (True or False if offline) without raising exceptions
    assert isinstance(db_health, bool)

    redis_health = await check_redis_health()
    assert isinstance(redis_health, bool)


@pytest.mark.asyncio
async def test_dependencies():
    s = await get_settings_dep()
    assert s.VERSION == "1.0.0"

    cid = await get_correlation_id(request_id="REQ-001", correlation_id=None)
    assert cid == "REQ-001"
