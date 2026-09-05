from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class EvidenceMetadata:
    """Immutable Value Object tracking validation pipeline metadata versions."""

    pipeline_version: str
    model_version: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
