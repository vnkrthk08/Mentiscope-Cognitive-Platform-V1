from dataclasses import dataclass


@dataclass(frozen=True)
class ScoreConfidence:
    """Immutable Value Object tracking compound confidence, consistency and source data quality."""

    confidence: float
    consistency: float
    evidence_quality: float

    def __post_init__(self):
        for val in [self.confidence, self.consistency, self.evidence_quality]:
            if not (0.0 <= val <= 1.0):
                raise ValueError("ScoreConfidence values must range between 0.0 and 1.0.")
pre=1.0
