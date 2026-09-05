"""ScoreExplanation Value Object."""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class ScoreExplanation:
    """Traceable scoring explanation breakdown for construct and framework scores."""

    framework_name: str
    construct_name: str
    raw_score: float
    normalized_score: float
    weight: float
    scoring_policy_id: str
    confidence: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "framework_name": self.framework_name,
            "construct_name": self.construct_name,
            "raw_score": self.raw_score,
            "normalized_score": self.normalized_score,
            "weight": self.weight,
            "scoring_policy_id": self.scoring_policy_id,
            "confidence": self.confidence,
        }
