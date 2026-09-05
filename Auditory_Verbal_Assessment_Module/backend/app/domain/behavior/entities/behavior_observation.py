from dataclasses import dataclass, field
from typing import List
from app.domain.behavior.value_objects.quote_reference import QuoteReference
from app.domain.behavior.value_objects.evidence_confidence import EvidenceConfidence


@dataclass
class BehaviorObservation:
    """Domain Entity representing a singular observation of behavioral traits during assessment."""

    observation_id: str
    behavior_type: str
    description: str
    supporting_quotes: List[QuoteReference]
    confidence: EvidenceConfidence
    linked_constructs: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.observation_id or not self.observation_id.strip():
            raise ValueError("BehaviorObservation observation_id cannot be empty.")
        if not self.behavior_type or not self.behavior_type.strip():
            raise ValueError("BehaviorObservation behavior_type cannot be empty.")
        if not self.description or not self.description.strip():
            raise ValueError("BehaviorObservation description cannot be empty.")
        if not self.supporting_quotes:
            raise ValueError("BehaviorObservation supporting_quotes cannot be empty.")
