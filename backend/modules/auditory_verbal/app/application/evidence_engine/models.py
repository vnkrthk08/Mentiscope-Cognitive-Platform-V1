from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import uuid


@dataclass(frozen=True)
class BehavioralQuote:
    quote: str
    segment_id: int = 0
    start_time: float = 0.0
    end_time: float = 0.0
    speaker: str = "CANDIDATE"


@dataclass(frozen=True)
class BehavioralObservation:
    observation: str
    reasoning: str
    quote: BehavioralQuote
    construct: str
    evidence_reference: str


@dataclass(frozen=True)
class BehavioralIndicator:
    name: str
    value: str
    supporting_evidence_ids: List[str]
    confidence: float


@dataclass(frozen=True)
class BehavioralEvidence:
    evidence_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    construct: str = "COMMUNICATION"
    behavior: str = ""
    observation: str = ""
    supporting_quote: Optional[BehavioralQuote] = None
    transcript_location: str = "0.0s - 10.0s"
    confidence: float = 0.95
    extraction_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    source_prompt_version: str = "1.0.0"
    model_version: str = "gemini-1.5-pro"


@dataclass(frozen=True)
class BehavioralEvidenceSet:
    """Immutable aggregate root representing a complete set of extracted evidence for a session."""

    evidence_set_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    scenario_id: str = ""
    prompt_id: str = ""
    transcript_version: str = "1.0.0"
    evidence_version: str = "1.0.0"
    evidence_items: List[BehavioralEvidence] = field(default_factory=list)
    indicators: List[BehavioralIndicator] = field(default_factory=list)
    extraction_metadata: Dict[str, Any] = field(default_factory=dict)
    schema_version: str = "1.0.0"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
