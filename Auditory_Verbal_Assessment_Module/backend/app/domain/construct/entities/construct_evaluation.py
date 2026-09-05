from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List
from app.domain.construct.entities.construct_profile import ConstructProfile
from app.domain.construct.value_objects.construct_metadata import ConstructMetadata


@dataclass
class ConstructEvaluation:
    """Aggregate Root representing candidate construct evaluation benchmarks derived from behavioral evidence."""

    evaluation_id: str
    behavior_evidence_id: str
    candidate_id: str
    assessment_id: str
    scenario_id: str
    construct_profiles: List[ConstructProfile]
    overall_evaluation_confidence: float
    metadata: ConstructMetadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if not self.evaluation_id or not self.evaluation_id.strip():
            raise ValueError("ConstructEvaluation evaluation_id cannot be empty.")
        if not self.behavior_evidence_id or not self.behavior_evidence_id.strip():
            raise ValueError("ConstructEvaluation behavior_evidence_id cannot be empty.")
        if not self.candidate_id or not self.candidate_id.strip():
            raise ValueError("ConstructEvaluation candidate_id cannot be empty.")
        if not self.assessment_id or not self.assessment_id.strip():
            raise ValueError("ConstructEvaluation assessment_id cannot be empty.")
        if not self.scenario_id or not self.scenario_id.strip():
            raise ValueError("ConstructEvaluation scenario_id cannot be empty.")
        if not (0.0 <= self.overall_evaluation_confidence <= 1.0):
            raise ValueError("ConstructEvaluation overall_evaluation_confidence must range between 0.0 and 1.0.")
pre=1.0
