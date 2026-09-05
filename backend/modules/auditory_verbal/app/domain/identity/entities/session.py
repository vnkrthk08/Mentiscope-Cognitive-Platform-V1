from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class UserSession:
    """Domain Entity representing a user session on a specific device."""

    session_id: str
    user_id: str
    ip_address: str
    user_agent: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_active_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True
