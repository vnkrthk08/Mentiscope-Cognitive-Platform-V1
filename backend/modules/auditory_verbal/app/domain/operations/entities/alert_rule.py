"""AlertRule Entity."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid


@dataclass
class AlertRule:
    """Configurable alert rule for operational thresholds."""

    rule_name: str
    metric_name: str  # api_latency, error_rate, storage_capacity, queue_backlog, provider_failure
    condition: str  # GT, LT, GTE, LTE, EQ
    threshold: float
    severity: str = "WARNING"  # INFO, WARNING, CRITICAL
    is_enabled: bool = True
    cooldown_seconds: int = 300
    rule_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.rule_name:
            raise ValueError("AlertRule rule_name cannot be empty.")
        if not self.metric_name:
            raise ValueError("AlertRule metric_name cannot be empty.")
        if self.condition not in ("GT", "LT", "GTE", "LTE", "EQ"):
            raise ValueError(f"Invalid condition: {self.condition}")
        if self.severity not in ("INFO", "WARNING", "CRITICAL"):
            raise ValueError(f"Invalid severity: {self.severity}")

    def evaluate(self, current_value: float) -> bool:
        """Returns True if the alert condition is triggered."""
        if not self.is_enabled:
            return False
        if self.condition == "GT":
            return current_value > self.threshold
        elif self.condition == "LT":
            return current_value < self.threshold
        elif self.condition == "GTE":
            return current_value >= self.threshold
        elif self.condition == "LTE":
            return current_value <= self.threshold
        elif self.condition == "EQ":
            return current_value == self.threshold
        return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "metric_name": self.metric_name,
            "condition": self.condition,
            "threshold": self.threshold,
            "severity": self.severity,
            "is_enabled": self.is_enabled,
            "cooldown_seconds": self.cooldown_seconds,
            "created_at": self.created_at.isoformat(),
        }
