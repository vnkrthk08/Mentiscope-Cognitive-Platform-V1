from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    """Base Domain Event class for all assessment lifecycle events."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
