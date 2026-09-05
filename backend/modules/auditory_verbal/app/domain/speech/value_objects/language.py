from dataclasses import dataclass


@dataclass(frozen=True)
class Language:
    """Immutable Value Object tracking language code classification."""

    language_code: str
    confidence: float

    def __post_init__(self):
        if not self.language_code or not self.language_code.strip():
            raise ValueError("Language language_code cannot be empty.")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("Language classification confidence must range between 0.0 and 1.0.")
