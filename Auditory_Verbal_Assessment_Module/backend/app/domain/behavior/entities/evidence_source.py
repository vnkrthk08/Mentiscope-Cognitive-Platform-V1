from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class EvidenceSource:
    """Domain Entity representing origin metrics metadata of behavioral analysis."""

    source_type: str
    source_id: str
    provider: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if not self.source_type or not self.source_type.strip():
            raise ValueError("EvidenceSource source_type cannot be empty.")
        if not self.source_id or not self.source_id.strip():
            raise ValueError("EvidenceSource source_id cannot be empty.")
        if not self.provider or not self.provider.strip():
            raise ValueError("EvidenceSource provider cannot be empty.")
