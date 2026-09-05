from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class ScoringMetadata:
    """Immutable Value Object tracking evaluation framework, pipeline, policy versions."""

    framework_version: str
    scoring_policy_version: str
    pipeline_version: str
    engine_version: str
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
pre=1.0
