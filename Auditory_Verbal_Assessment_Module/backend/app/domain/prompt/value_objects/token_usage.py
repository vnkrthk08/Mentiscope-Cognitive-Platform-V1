from dataclasses import dataclass


@dataclass(frozen=True)
class TokenUsage:
    """Immutable Value Object tracking input, output and estimated cost values of LLM calls."""

    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost_usd: float

    def __post_init__(self):
        if self.input_tokens < 0 or self.output_tokens < 0 or self.total_tokens < 0:
            raise ValueError("TokenUsage parameter counts must be positive.")
        if self.estimated_cost_usd < 0:
            raise ValueError("TokenUsage cost parameter must be positive.")
