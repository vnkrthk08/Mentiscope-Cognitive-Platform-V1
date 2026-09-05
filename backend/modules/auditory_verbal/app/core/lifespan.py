from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.database import check_database_health
from app.core.redis import init_redis, close_redis, check_redis_health
from app.infrastructure.platform_integration import PlatformIntegrationManager
from app.application.identity.services.auth_service import AuthService


from app.infrastructure.persistence.database.engine import engine
from app.infrastructure.persistence.database.base import Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager managing startup and shutdown tasks."""
    # 1. Startup
    setup_logging()
    logger.info(f"=== Starting {settings.PROJECT_NAME} (v{settings.VERSION}) [{settings.ENVIRONMENT}] ===")

    # Ensure database schema is fully created
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("[LIFESPAN] Database tables verified/created successfully.")
    except Exception as db_err:
        logger.error(f"[LIFESPAN] Database table creation failed: {db_err}")

    # Initialize Redis client
    await init_redis()

    # Initialize Platform Integration Manager & Subsystems
    platform_mgr = PlatformIntegrationManager()
    await platform_mgr.initialize_platform(env=settings.ENVIRONMENT.value)
    app.state.platform_manager = platform_mgr

    # Check database and Redis readiness
    db_ok = await check_database_health()
    redis_ok = await check_redis_health()
    logger.info(f"[LIFESPAN] Database Status: {'HEALTHY' if db_ok else 'UNAVAILABLE (Using In-Memory/Fallback)'}")
    logger.info(f"[LIFESPAN] Redis Status: {'HEALTHY' if redis_ok else 'UNAVAILABLE (Using In-Memory/Fallback)'}")

    # Seed baseline roles and permission mappings
    try:
        await AuthService.seed_roles_and_permissions()
        logger.info("[LIFESPAN] baseline identity roles and permissions seeded successfully.")
    except Exception as e:
        logger.warning(f"[LIFESPAN] Seeding roles and permissions failed: {str(e)}")

    # 10. Startup Diagnostics and Connectivity Validations
    provider = settings.LLM_PROVIDER
    model = ""
    api_key_loaded = "No"

    if provider.lower() == "gemini":
        model = settings.GEMINI_MODEL
        api_key_loaded = "Yes" if settings.GEMINI_API_KEY else "No"
    elif provider.lower() == "openai":
        model = settings.OPENAI_MODEL
        api_key_loaded = "Yes" if settings.OPENAI_API_KEY else "No"
    elif provider.lower() == "claude":
        model = settings.CLAUDE_MODEL
        api_key_loaded = "Yes" if settings.ANTHROPIC_API_KEY else "No"
    elif provider.lower() in ("openrouter", "nvidia"):
        model = settings.OPENROUTER_MODEL
        api_key_loaded = "Yes" if settings.OPENROUTER_API_KEY else "No"

    logger.info("======== LLM Configuration ========")
    logger.info(f"Environment: {settings.ENVIRONMENT.value}")
    logger.info(f"Provider: {provider}")
    logger.info(f"Selected Model: {model}")
    logger.info(f"LLM Mode: {settings.LLM_MODE}")
    logger.info(f"API Key Loaded (Yes/No): {api_key_loaded}")
    logger.info(f"Speech Provider: {settings.SPEECH_PROVIDER}")
    logger.info("===================================")

    from app.infrastructure.prompt.provider_registry import llm_registry
    from datetime import datetime, timezone

    try:
        if settings.LLM_MODE == "real":
            provider_name = settings.LLM_PROVIDER.lower()
            logger.info(f"[LIFESPAN] Validating real LLM provider configuration for '{provider_name}'...")
            
            if not model:
                raise ValueError(f"Model for real provider '{provider_name}' is not configured.")
            if api_key_loaded == "No":
                raise ValueError(f"Required API key for real provider '{provider_name}' is missing.")
                
            provider_inst = llm_registry.get_provider(provider_name)
            
            logger.info(f"[LIFESPAN] Testing connectivity to real LLM provider '{provider_name}'...")
            health_ok = await provider_inst.health_check()
            if not health_ok:
                raise RuntimeError(f"Connectivity check to real LLM provider '{provider_name}' failed. Verify API key and internet connection.")
                
            logger.info(f"[LIFESPAN] Real LLM provider '{provider_name}' initialized and connected successfully.")
        
        # Mark initialized in registry
        llm_registry.initialized = True
        llm_registry.last_successful_init = datetime.now(timezone.utc).isoformat()
        llm_registry.latest_error = None

    except Exception as llm_err:
        logger.error(f"[LIFESPAN] LLM Initialization failed: {str(llm_err)}")
        llm_registry.initialized = False
        llm_registry.latest_error = str(llm_err)
        
        if settings.LLM_MODE == "real":
            logger.error("[LIFESPAN] Aborting startup due to real LLM initialization failure.")
            raise llm_err

    yield

    # 2. Graceful Shutdown
    logger.info(f"=== Stopping {settings.PROJECT_NAME} ===")
    await platform_mgr.shutdown_platform(reason="FASTAPI_SHUTDOWN")
    await close_redis()
    logger.info("[LIFESPAN] Connection pools closed. Shutdown complete.")
