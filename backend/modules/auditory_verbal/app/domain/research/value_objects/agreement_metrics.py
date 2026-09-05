"""
AgreementMetrics Value Object.

Stores the raw inter-rater agreement data between AI scores and
expert reviewer scores for a single dataset record. The actual
statistical significance testing (ICC, Cohen's Kappa, Cronbach Alpha)
is performed externally by psychologists on the exported dataset.

This VO only stores the raw inputs needed for those calculations.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class AgreementMetrics:
    """
    Raw agreement data between AI-generated scores and expert-assigned scores.

    No reliability statistics are computed here.
    All analysis is deferred to external psychometric tools.
    """

    ai_construct_scores: Dict[str, float]
    expert_construct_scores: Dict[str, float]
    reviewer_id: str
    review_round: int = 1
    score_deltas: Dict[str, float] = field(default_factory=dict)
    discrepant_constructs: List[str] = field(default_factory=list)
    agreement_flag: str = "PENDING"   # AGREEMENT | DISCREPANT | PARTIAL
    notes: Optional[str] = None

    def __post_init__(self) -> None:
        if not self.ai_construct_scores:
            raise ValueError("AgreementMetrics: ai_construct_scores cannot be empty.")
        if not self.reviewer_id:
            raise ValueError("AgreementMetrics: reviewer_id is required.")
        if self.review_round < 1:
            raise ValueError("AgreementMetrics: review_round must be >= 1.")

    def compute_deltas(self) -> Dict[str, float]:
        """Return absolute score difference per construct (AI minus Expert)."""
        return {
            construct: round(self.ai_construct_scores.get(construct, 0.0)
                             - self.expert_construct_scores.get(construct, 0.0), 4)
            for construct in set(self.ai_construct_scores) | set(self.expert_construct_scores)
        }

    def to_dict(self) -> dict:
        return {
            "ai_construct_scores": self.ai_construct_scores,
            "expert_construct_scores": self.expert_construct_scores,
            "reviewer_id": self.reviewer_id,
            "review_round": self.review_round,
            "score_deltas": self.score_deltas,
            "discrepant_constructs": self.discrepant_constructs,
            "agreement_flag": self.agreement_flag,
            "notes": self.notes,
        }
