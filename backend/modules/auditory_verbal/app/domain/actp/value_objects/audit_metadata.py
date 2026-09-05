"""AuditMetadata Value Object."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class AuditMetadata:
    """Immutable audit metadata containing environment, IP, user_agent, and versioning info."""

    environment: str = "production"
    ip_address: str = "127.0.0.1"
    user_agent: str = "Mentiscope-Pipeline/1.0"
    schema_version: str = "1.0.0"
    tags: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "environment": self.environment,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "schema_version": self.schema_version,
            "tags": dict(self.tags) if self.tags else {},
        }
