from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict


@dataclass
class AuditLog:
    """Domain Entity representing a structured security / identity audit log record."""

    log_id: str
    actor: str
    action: str
    target: str
    ip_address: str
    user_agent: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if not self.log_id or not self.log_id.strip():
            raise ValueError("AuditLog log_id cannot be empty.")
        if not self.actor or not self.actor.strip():
            raise ValueError("AuditLog actor cannot be empty.")
        if not self.action or not self.action.strip():
            raise ValueError("AuditLog action cannot be empty.")
