import time
from typing import Optional, Dict
from app.core.redis import redis_client


class TokenStore:
    """Caching service interacting with Redis for token blacklisting, sessions, and rate limiting.
    Falls back gracefully to an in-memory dictionary if Redis is offline/unavailable.
    """

    def __init__(self):
        self._in_memory_blacklist: Dict[str, float] = {}
        self._in_memory_failed_logins: Dict[str, Dict[str, float]] = {}

    async def blacklist_jti(self, jti: str, expires_in_seconds: int) -> None:
        if redis_client:
            try:
                await redis_client.setex(f"blacklist:{jti}", expires_in_seconds, "1")
                return
            except Exception:
                pass
        self._in_memory_blacklist[jti] = time.time() + expires_in_seconds

    async def is_jti_blacklisted(self, jti: str) -> bool:
        if redis_client:
            try:
                res = await redis_client.get(f"blacklist:{jti}")
                return res is not None
            except Exception:
                pass
        exp = self._in_memory_blacklist.get(jti)
        if exp:
            if time.time() > exp:
                del self._in_memory_blacklist[jti]
                return False
            return True
        return False

    async def track_failed_login(self, username_or_ip: str) -> int:
        """Tracks consecutive failed login attempts, returning the current counter."""
        if redis_client:
            try:
                key = f"failed_login:{username_or_ip}"
                count = await redis_client.incr(key)
                if count == 1:
                    await redis_client.expire(key, 900)  # 15 minutes window
                return count
            except Exception:
                pass

        # Fallback tracking
        now = time.time()
        record = self._in_memory_failed_logins.get(username_or_ip)
        if not record or now > record["reset_at"]:
            record = {"count": 1, "reset_at": now + 900}
            self._in_memory_failed_logins[username_or_ip] = record
        else:
            record["count"] += 1
        return record["count"]

    async def reset_failed_logins(self, username_or_ip: str) -> None:
        if redis_client:
            try:
                await redis_client.delete(f"failed_login:{username_or_ip}")
                return
            except Exception:
                pass
        if username_or_ip in self._in_memory_failed_logins:
            del self._in_memory_failed_logins[username_or_ip]


# Singleton instance
token_store = TokenStore()
