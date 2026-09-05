"""HealthCheck Entity."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid

from app.domain.operations.value_objects.service_health import ServiceHealth
from app.domain.operations.value_objects.system_status import SystemStatus


@dataclass
class HealthCheck:
    """Complete platform health check result aggregating all service statuses."""

    system_status: SystemStatus
    services: List[ServiceHealth] = field(default_factory=list)
    check_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    checked_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def overall_status(self) -> str:
        if not self.services:
            return self.system_status.status
        statuses = [s.status for s in self.services]
        if all(s == "HEALTHY" for s in statuses):
            return "HEALTHY"
        if any(s == "UNAVAILABLE" for s in statuses):
            return "CRITICAL"
        return "DEGRADED"

    @property
    def healthy_count(self) -> int:
        return sum(1 for s in self.services if s.status == "HEALTHY")

    @property
    def degraded_count(self) -> int:
        return sum(1 for s in self.services if s.status == "DEGRADED")

    @property
    def unavailable_count(self) -> int:
        return sum(1 for s in self.services if s.status == "UNAVAILABLE")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "check_id": self.check_id,
            "overall_status": self.overall_status,
            "system_status": self.system_status.to_dict(),
            "services": [s.to_dict() for s in self.services],
            "healthy_count": self.healthy_count,
            "degraded_count": self.degraded_count,
            "unavailable_count": self.unavailable_count,
            "checked_at": self.checked_at.isoformat(),
        }
