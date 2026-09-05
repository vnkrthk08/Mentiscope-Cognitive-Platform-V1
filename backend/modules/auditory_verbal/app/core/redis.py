from typing import Optional, Any
from app.core.config import settings
from app.core.logging import logger

try:
    from redis.asyncio import Redis, ConnectionPool
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False
    Redis = None
    ConnectionPool = None

# Global Redis Client singleton and connection pool
redis_pool: Optional[Any] = None
redis_client: Optional[Any] = None


async def init_redis() -> Optional[Any]:
    """Initializes async Redis connection pool and client."""
    global redis_pool, redis_client
    if not HAS_REDIS:
        logger.warning("[REDIS] redis-py package not installed. Redis client disabled.")
        return None
    try:
        redis_pool = ConnectionPool.from_url(
            settings.active_redis_url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
        )
        redis_client = Redis(connection_pool=redis_pool)
        # Verify ping
        await redis_client.ping()
        logger.info(f"[REDIS] Redis client successfully connected to {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        return redis_client
    except Exception as e:
        logger.warning(f"[REDIS] Failed to connect to Redis server ({settings.active_redis_url}): {str(e)}")
        redis_client = None
        return None


async def close_redis():
    """Closes Redis connection pool cleanly."""
    global redis_client, redis_pool
    if redis_client:
        try:
            await redis_client.close()
        except Exception:
            pass
        redis_client = None
    if redis_pool:
        try:
            await redis_pool.disconnect()
        except Exception:
            pass
        redis_pool = None
    logger.info("[REDIS] Redis connection pool disconnected.")


async def check_redis_health() -> bool:
    """Verifies Redis ping response."""
    global redis_client
    if not HAS_REDIS or not redis_client:
        return False
    try:
        return await redis_client.ping() is True
    except Exception as e:
        logger.warning(f"[REDIS HEALTH CHECK] Redis ping failed: {str(e)}")
        return False
