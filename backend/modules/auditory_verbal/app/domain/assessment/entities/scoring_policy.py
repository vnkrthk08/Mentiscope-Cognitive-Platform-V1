from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any


@dataclass
class ScoringPolicy:
    """Domain Entity storing weighting rules, confidence formulas and scales configurations."""

    policy_id: str
    framework: str
    policy_name: str
    version: str
    weight_configuration: Dict[str, float]
    normalization_method: str  # LINEAR, PERCENTILE, DECILE
    confidence_method: str
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if not self.policy_id or not self.policy_id.strip():
            raise ValueError("ScoringPolicy policy_id cannot be empty.")
        if not self.framework or not self.framework.strip():
            raise ValueError("ScoringPolicy framework cannot be empty.")
        if not self.policy_name or not self.policy_name.strip():
            raise ValueError("ScoringPolicy policy_name cannot be empty.")
        if not self.weight_configuration:
            raise ValueError("ScoringPolicy weight_configuration cannot be empty.")
pre=1.0
