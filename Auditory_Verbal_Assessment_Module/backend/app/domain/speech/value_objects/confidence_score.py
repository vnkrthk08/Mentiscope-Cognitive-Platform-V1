from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True)
class ConfidenceScore:
    """Immutable Value Object calculating transcription overall and word-level accuracy logs."""

    overall_score: float
    per_word_scores: List[float] = field(default_factory=list)

    def __post_init__(self):
        if not (0.0 <= self.overall_score <= 1.0):
            raise ValueError("ConfidenceScore overall_score must range between 0.0 and 1.0.")
        for score in self.per_word_scores:
            if not (0.0 <= score <= 1.0):
                raise ValueError("Per-word confidence score must range between 0.0 and 1.0.")
        # Automatically calculate overall score fallback if empty
        if not self.per_word_scores and self.overall_score == 0.0:
            object.__setattr__(self, "overall_score", 1.0)
