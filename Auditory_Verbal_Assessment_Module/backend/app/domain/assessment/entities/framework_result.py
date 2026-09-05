from dataclasses import dataclass
from typing import List
from app.domain.assessment.entities.score_breakdown import ScoreBreakdown


@dataclass
class FrameworkResult:
    """Domain Entity aggregating scoring profiles per assessment framework model."""

    framework: str
    raw_score: float
    normalized_score: float
    confidence: float
    construct_results: List[ScoreBreakdown]
    supporting_evidence_count: int
    policy_version: str
    summary: str

    def __post_init__(self):
        if not self.framework or not self.framework.strip():
            raise ValueError("FrameworkResult framework cannot be empty.")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("FrameworkResult confidence must range between 0.0 and 1.0.")
        if not self.construct_results:
            raise ValueError("FrameworkResult construct_results list cannot be empty.")
pre=1.0
