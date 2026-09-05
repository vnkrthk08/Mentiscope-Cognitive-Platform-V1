from dataclasses import dataclass


@dataclass(frozen=True)
class ContextWindow:
    """Immutable Value Object storing contextual capacity parameters of target LLM."""

    max_tokens: int
    current_tokens: int

    def __post_init__(self):
        if self.max_tokens <= 0 or self.current_tokens < 0:
            raise ValueError("ContextWindow tokens parameters must be positive.")
        if self.current_tokens > self.max_tokens:
            raise ValueError("ContextWindow current_tokens exceeds max_tokens capacity.")
