from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
from app.domain.value_objects.confidence_level import ConfidenceLevel
from app.domain.value_objects.enums import ConstructType, EvidenceType, PolarityType


@dataclass
class Evidence:
    """Entity representing structured observable evidence extracted by AI/rule engine."""

    evidence_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    prompt_id: str = ""
    construct: ConstructType = ConstructType.WORKING_MEMORY
    quote: str = ""
    indicator_description: str = ""
    confidence: ConfidenceLevel = field(default=ConfidenceLevel(0.95))
    polarity: PolarityType = PolarityType.POSITIVE
    evidence_type: EvidenceType = EvidenceType.VERBATIM_QUOTE
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if not self.session_id or not self.session_id.strip():
            raise ValueError("Evidence session_id cannot be empty.")
        if not self.prompt_id or not self.prompt_id.strip():
            raise ValueError("Evidence prompt_id cannot be empty.")
        if not self.quote or not self.quote.strip():
            raise ValueError("Evidence quote cannot be empty.")
        if not self.indicator_description or not self.indicator_description.strip():
            raise ValueError("Evidence indicator_description cannot be empty.")
