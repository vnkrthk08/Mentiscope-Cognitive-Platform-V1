from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class ConstructMetadata:
    """Immutable Value Object tracking versions of assessment framework configurations."""

    framework_version: str
    pipeline_version: str
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
pre=1.0
