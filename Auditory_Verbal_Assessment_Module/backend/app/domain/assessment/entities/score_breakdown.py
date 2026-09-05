from dataclasses import dataclass
from typing import List
from app.domain.assessment.value_objects.score_reference import ScoreReference


@dataclass
class ScoreBreakdown:
    """Domain Entity detailing scores and confidence for a specific psychometric construct."""

    construct: str
    raw_score: float
    normalized_score: float
    confidence: float
    support_strength: float
    evidence_count: int
    references: List[ScoreReference]

    def __post_init__(self):
        if not self.construct or not self.construct.strip():
            raise ValueError("ScoreBreakdown construct name cannot be empty.")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("ScoreBreakdown confidence must range between 0.0 and 1.0.")
        if self.evidence_count < 0:
            raise ValueError("ScoreBreakdown evidence_count must be positive.")
pre=1.0
