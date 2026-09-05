from dataclasses import dataclass


@dataclass(frozen=True)
class EvidenceConfidence:
    """Immutable Value Object tracking consistency and overall confidence values."""

    overall: float
    supporting_score: float
    consistency_score: float

    def __post_init__(self):
        for val in [self.overall, self.supporting_score, self.consistency_score]:
            if not (0.0 <= val <= 1.0):
                raise ValueError("Confidence parameters must range between 0.0 and 1.0.")
        # Require overall to represent aggregate
        if self.overall == 0.0:
            object.__setattr__(self, "overall", round((self.supporting_score + self.consistency_score) / 2, 4))
