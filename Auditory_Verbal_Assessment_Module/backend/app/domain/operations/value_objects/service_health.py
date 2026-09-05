"""ServiceHealth Value Object."""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class ServiceHealth:
    """Health status for an individual platform service or dependency."""

    service_name: str
    status: str  # HEALTHY, DEGRADED, UNAVAILABLE, UNKNOWN
    latency_ms: float = 0.0
    last_checked: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "service_name": self.service_name,
            "status": self.status,
            "latency_ms": self.latency_ms,
            "last_checked": self.last_checked,
            "details": self.details,
        }
