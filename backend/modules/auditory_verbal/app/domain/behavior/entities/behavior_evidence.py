from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List
from app.domain.behavior.entities.behavior_observation import BehaviorObservation
from app.domain.behavior.entities.evidence_source import EvidenceSource
from app.domain.behavior.value_objects.evidence_metadata import EvidenceMetadata


@dataclass
class BehaviorEvidence:
    """Aggregate Root managing the structured collection of validated behavioral evidence indicators."""

    evidence_id: str
    transcript_id: str
    prompt_execution_id: str
    candidate_id: str
    assessment_id: str
    scenario_id: str
    construct_candidates: List[str]
    behavior_observations: List[BehaviorObservation]
    evidence_sources: List[EvidenceSource]
    overall_confidence: float
    metadata: EvidenceMetadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if not self.evidence_id or not self.evidence_id.strip():
            raise ValueError("BehaviorEvidence evidence_id cannot be empty.")
        if not self.transcript_id or not self.transcript_id.strip():
            raise ValueError("BehaviorEvidence transcript_id cannot be empty.")
        if not self.prompt_execution_id or not self.prompt_execution_id.strip():
            raise ValueError("BehaviorEvidence prompt_execution_id cannot be empty.")
        if not self.candidate_id or not self.candidate_id.strip():
            raise ValueError("BehaviorEvidence candidate_id cannot be empty.")
        if not self.assessment_id or not self.assessment_id.strip():
            raise ValueError("BehaviorEvidence assessment_id cannot be empty.")
        if not self.scenario_id or not self.scenario_id.strip():
            raise ValueError("BehaviorEvidence scenario_id cannot be empty.")
        if not (0.0 <= self.overall_confidence <= 1.0):
            raise ValueError("BehaviorEvidence overall_confidence must range between 0.0 and 1.0.")
