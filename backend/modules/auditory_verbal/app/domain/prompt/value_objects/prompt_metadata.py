from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class PromptMetadata:
    """Immutable Value Object tracking template normalization versions."""

    normalization_version: str
    pipeline_version: str
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
