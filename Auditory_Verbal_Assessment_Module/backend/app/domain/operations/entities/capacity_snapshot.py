"""CapacitySnapshot Entity."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict
import uuid


@dataclass
class CapacitySnapshot:
    """Point-in-time capacity and resource utilization snapshot for capacity planning."""

    cpu_percent: float
    memory_percent: float
    disk_percent: float
    db_connections_active: int
    db_connections_max: int
    api_requests_per_minute: float
    avg_api_latency_ms: float
    pipeline_throughput_per_hour: float
    assessment_completion_rate: float
    error_rate_percent: float
    snapshot_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    captured_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def db_utilization_percent(self) -> float:
        if self.db_connections_max == 0:
            return 0.0
        return round((self.db_connections_active / self.db_connections_max) * 100, 2)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "cpu_percent": self.cpu_percent,
            "memory_percent": self.memory_percent,
            "disk_percent": self.disk_percent,
            "db_connections_active": self.db_connections_active,
            "db_connections_max": self.db_connections_max,
            "db_utilization_percent": self.db_utilization_percent,
            "api_requests_per_minute": self.api_requests_per_minute,
            "avg_api_latency_ms": self.avg_api_latency_ms,
            "pipeline_throughput_per_hour": self.pipeline_throughput_per_hour,
            "assessment_completion_rate": self.assessment_completion_rate,
            "error_rate_percent": self.error_rate_percent,
            "captured_at": self.captured_at.isoformat(),
        }
