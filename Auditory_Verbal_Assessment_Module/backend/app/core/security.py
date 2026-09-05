import base64
import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from app.core.config import settings
from app.core.constants import ALGORITHM_HS256, DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES

try:
    import jwt
    HAS_JWT = True
except ImportError:
    HAS_JWT = False


class SecurityUtils:
    """Security utilities for hashing passwords and encoding/decoding JWT tokens."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Hashes plain password using SHA-256 with salt abstraction."""
        salted = f"{settings.SECRET_KEY}:{password}".encode("utf-8")
        return hashlib.sha256(salted).hexdigest()

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifies plain password against hashed password string."""
        return SecurityUtils.hash_password(plain_password) == hashed_password

    @staticmethod
    def create_access_token(
        subject: str, expires_delta: Optional[timedelta] = None, claims: Optional[Dict[str, Any]] = None
    ) -> str:
        """Encodes subject string and claims into JWT access token."""
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode: Dict[str, Any] = {"sub": subject, "exp": expire.isoformat() if not HAS_JWT else expire, "iat": datetime.now(timezone.utc).isoformat() if not HAS_JWT else datetime.now(timezone.utc)}
        if claims:
            to_encode.update(claims)

        if HAS_JWT:
            encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
            return encoded_jwt
        else:
            # Fallback lightweight token encoding for environment without pyjwt
            raw = json.dumps(to_encode).encode("utf-8")
            b64_payload = base64.urlsafe_b64encode(raw).decode("utf-8")
            signature = hashlib.sha256(f"{b64_payload}:{settings.SECRET_KEY}".encode("utf-8")).hexdigest()[:16]
            return f"bearer.{b64_payload}.{signature}"

    @staticmethod
    def decode_access_token(token: str) -> Dict[str, Any]:
        """Decodes JWT access token and returns payload dict."""
        if HAS_JWT:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        else:
            parts = token.split(".")
            if len(parts) == 3 and parts[0] == "bearer":
                b64_payload = parts[1]
                raw = base64.urlsafe_b64decode(b64_payload.encode("utf-8")).decode("utf-8")
                return json.loads(raw)
            raise ValueError("Invalid token format")
