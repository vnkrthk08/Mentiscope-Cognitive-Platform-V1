from dataclasses import dataclass


@dataclass(frozen=True)
class TimeLimit:
    """Immutable Value Object representing prompt and response time constraints."""

    max_seconds: int
    grace_period_seconds: int = 5

    def __post_init__(self):
        if self.max_seconds <= 0:
            raise ValueError("Time limit max_seconds must be positive.")
        if self.grace_period_seconds < 0:
            raise ValueError("Grace period seconds cannot be negative.")
