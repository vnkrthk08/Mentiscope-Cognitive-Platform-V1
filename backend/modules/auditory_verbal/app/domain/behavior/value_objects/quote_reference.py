from dataclasses import dataclass


@dataclass(frozen=True)
class QuoteReference:
    """Immutable Value Object storing speech segments citation, indices and timestamps."""

    quote: str
    start_word_index: int
    end_word_index: int
    start_time: float
    end_time: float

    def __post_init__(self):
        if self.start_word_index < 0 or self.end_word_index < 0 or self.end_word_index < self.start_word_index:
            raise ValueError("QuoteReference word indices must be positive and ordered.")
        if self.start_time < 0 or self.end_time < 0 or self.end_time < self.start_time:
            raise ValueError("QuoteReference timestamps must be positive and ordered.")
