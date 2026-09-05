"""SystemStatus Value Object."""
from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class SystemStatus:
    """Immutable system-level status snapshot."""

    status: str  # HEALTHY, DEGRADED, CRITICAL, MAINTENANCE
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    disk_percent: float = 0.0
    uptime_seconds: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "disk_percent": self.disk_percent,
            "uptime_seconds": self.uptime_seconds,
        }
