from dataclasses import dataclass


@dataclass(frozen=True)
class ConstructConfidence:
    """Immutable Value Object storing evaluation confidence scores."""

    confidence_score: float
    support_strength: float
    evidence_count: int

    def __post_init__(self):
        if not (0.0 <= self.confidence_score <= 1.0):
            raise ValueError("ConstructConfidence confidence_score must range between 0.0 and 1.0.")
        if not (0.0 <= self.support_strength <= 1.0):
            raise ValueError("ConstructConfidence support_strength must range between 0.0 and 1.0.")
        if self.evidence_count < 0:
            raise ValueError("ConstructConfidence evidence_count must be positive.")
        # Auto compute support strength if zero
        if self.support_strength == 0.0 and self.evidence_count > 0:
            object.__setattr__(self, "support_strength", min(1.0, self.evidence_count * 0.25))
        if self.confidence_score == 0.0:
            object.__setattr__(self, "confidence_score", self.support_strength)
pre=1.0
