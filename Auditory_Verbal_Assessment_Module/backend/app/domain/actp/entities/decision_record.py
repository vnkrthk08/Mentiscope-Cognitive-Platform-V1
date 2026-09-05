"""DecisionRecord Entity."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import json
from typing import Any, Dict, List, Optional
import uuid

from app.domain.actp.value_objects.evidence_reference import EvidenceReference
from app.domain.actp.value_objects.score_explanation import ScoreExplanation
from app.domain.actp.value_objects.pipeline_invocation import PipelineInvocation


@dataclass
class DecisionRecord:
    """Immutable, reproducible record of an automated or expert scoring decision."""

    decision_id: str
    assessment_id: str
    decision_type: str  # CONSTRUCT_RATING, FRAMEWORK_SCORE, POLICY_SELECTION, EXPERT_APPROVAL
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_decision: Dict[str, Any] = field(default_factory=dict)
    score_explanations: List[ScoreExplanation] = field(default_factory=list)
    evidence_references: List[EvidenceReference] = field(default_factory=list)
    pipeline_invocation: Optional[PipelineInvocation] = None
    reproducible_hash: str = field(init=False)
    record_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    recorded_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not self.decision_id:
            raise ValueError("DecisionRecord decision_id cannot be empty.")
        if not self.assessment_id:
            raise ValueError("DecisionRecord assessment_id cannot be empty.")

        # Compute SHA-256 reproducibility hash
        payload = {
            "decision_id": self.decision_id,
            "assessment_id": self.assessment_id,
            "input_data": self.input_data,
            "output_decision": self.output_decision,
        }
        serialized = json.dumps(payload, sort_keys=True, default=str)
        self.reproducible_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "decision_id": self.decision_id,
            "assessment_id": self.assessment_id,
            "decision_type": self.decision_type,
            "input_data": self.input_data,
            "output_decision": self.output_decision,
            "score_explanations": [se.to_dict() for se in self.score_explanations],
            "evidence_references": [er.to_dict() for er in self.evidence_references],
            "pipeline_invocation": self.pipeline_invocation.to_dict() if self.pipeline_invocation else None,
            "reproducible_hash": self.reproducible_hash,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
        }
