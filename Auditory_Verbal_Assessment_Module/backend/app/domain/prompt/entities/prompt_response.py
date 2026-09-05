from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class PromptResponse:
    """Domain Entity mapping the parsed and normalized JSON structure of an LLM call response."""

    response_id: str
    execution_id: str
    content_raw: str
    content_normalized: str  # Typically parsed JSON payload content
    received_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if not self.response_id or not self.response_id.strip():
            raise ValueError("PromptResponse response_id cannot be empty.")
        if not self.execution_id or not self.execution_id.strip():
            raise ValueError("PromptResponse execution_id cannot be empty.")
        if not self.content_raw or not self.content_raw.strip():
            raise ValueError("PromptResponse content_raw cannot be empty.")
