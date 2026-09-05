from dataclasses import dataclass


@dataclass(frozen=True)
class WordTimestamp:
    """Immutable Value Object tracking timings and confidence values of a single transcribed word."""

    word: str
    start_time: float
    end_time: float
    confidence: float

    def __post_init__(self):
        if not self.word or not self.word.strip():
            raise ValueError("WordTimestamp word cannot be empty.")
        if self.start_time < 0 or self.end_time < 0 or self.end_time < self.start_time:
            raise ValueError("WordTimestamp start/end timings must be positive and ordered.")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("WordTimestamp confidence must range between 0.0 and 1.0.")
