import uuid
import jwt
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
from app.core.config import settings


class JWTService:
    """Service responsible for encoding, decoding, signing, and validating RFC 7519 JWTs."""

    @staticmethod
    def create_access_token(
        user_id: str,
        role: str,
        permissions: List[str],
        session_id: str,
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        now = datetime.now(timezone.utc)
        if expires_delta:
            expire = now + expires_delta
        else:
            expire = now + timedelta(minutes=15)

        claims = {
            "sub": user_id,
            "role": role,
            "permissions": permissions,
            "session_id": session_id,
            "jti": str(uuid.uuid4()),  # Guarantee uniqueness of every token
            "iat": int(now.timestamp()),
            "exp": int(expire.timestamp()),
            "iss": "MentiScope",
            "aud": "mentiscope-api",
        }
        return jwt.encode(claims, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
                audience="mentiscope-api",
                issuer="MentiScope",
            )
            return payload
        except jwt.PyJWTError:
            return None
