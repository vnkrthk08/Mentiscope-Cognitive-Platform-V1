from dataclasses import dataclass


@dataclass(frozen=True)
class ConfidenceLevel:
    """Immutable Value Object enforcing confidence bounds [0.0, 1.0]."""

    score: float

    def __post_init__(self):
        if not (0.0 <= self.score <= 1.0):
            raise ValueError(f"Confidence score {self.score} must be between 0.0 and 1.0 inclusive.")
