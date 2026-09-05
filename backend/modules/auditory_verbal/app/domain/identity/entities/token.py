from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class RefreshToken:
    """Domain Entity representing a long-lived JWT refresh token record."""

    token_id: str
    user_id: str
    token: str
    expires_at: datetime
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_revoked: bool = False

    def is_expired(self) -> bool:
        expires = self.expires_at
        if expires.tzinfo is None:
            return datetime.now() > expires
        return datetime.now(timezone.utc) > expires


@dataclass
class PasswordResetToken:
    """Domain Entity representing a temporary password reset token."""

    token_id: str
    user_id: str
    token: str
    expires_at: datetime
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_used: bool = False

    def is_valid(self) -> bool:
        expires = self.expires_at
        now = datetime.now() if expires.tzinfo is None else datetime.now(timezone.utc)
        return not self.is_used and now <= expires


@dataclass
class EmailVerificationToken:
    """Domain Entity representing a candidate/user email verification token."""

    token_id: str
    user_id: str
    token: str
    expires_at: datetime
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_used: bool = False

    def is_valid(self) -> bool:
        expires = self.expires_at
        now = datetime.now() if expires.tzinfo is None else datetime.now(timezone.utc)
        return not self.is_used and now <= expires
