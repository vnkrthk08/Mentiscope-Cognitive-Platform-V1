from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass(frozen=True)
class ReportMetadata:
    """Immutable Value Object tracking generation details of reports."""

    generated_by: str
    pipeline_version: str
    engine_version: str
    report_version: str
    language: str
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if not self.generated_by or not self.generated_by.strip():
            raise ValueError("ReportMetadata generated_by cannot be empty.")
        if not self.language or not self.language.strip():
            raise ValueError("ReportMetadata language cannot be empty.")
pre=1.0
