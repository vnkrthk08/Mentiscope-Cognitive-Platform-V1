from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class TranscriptMetadata:
    """Immutable Value Object storing pipeline metadata information."""

    normalization_version: str
    provider_version: str
    processing_pipeline_version: str
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
