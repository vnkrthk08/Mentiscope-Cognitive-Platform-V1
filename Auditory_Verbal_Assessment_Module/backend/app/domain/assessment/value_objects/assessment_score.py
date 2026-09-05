from dataclasses import dataclass


@dataclass(frozen=True)
class AssessmentScore:
    """Immutable Value Object tracking raw, normalized and scale boundaries."""

    raw_score: float
    normalized_score: float
    score_scale: str

    def __post_init__(self):
        if self.raw_score < 0.0:
            raise ValueError("AssessmentScore raw_score must be positive.")
        if self.normalized_score < 0.0:
            raise ValueError("AssessmentScore normalized_score must be positive.")
        if not self.score_scale or not self.score_scale.strip():
            raise ValueError("AssessmentScore score_scale cannot be empty.")
pre=1.0
