from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import uuid


@dataclass(frozen=True)
class ConstructEvidenceSummary:
    construct: str
    evidence_count: int
    indicator_count: int
    evidence_references: List[str]
    observation_summary: str


@dataclass(frozen=True)
class ConstructEvaluation:
    evaluation_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    construct_name: str = "DECISION_MAKING"
    construct_description: str = "Ability to evaluate options and choose ethical, effective actions under pressure."
    behavioral_summary: str = ""
    supporting_evidence_ids: List[str] = field(default_factory=list)
    evaluation_narrative: str = ""
    evaluation_confidence: float = 0.95
    evaluation_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    prompt_version: str = "1.0.0"
    model_version: str = "gemini-1.5-pro"


@dataclass(frozen=True)
class ConstructAssessment:
    assessment_name: str
    interpretation: str
    strengths: List[str]
    development_areas: List[str]
    supporting_evaluations: List[str]


@dataclass(frozen=True)
class ConstructEvaluationSet:
    """Immutable aggregate root representing full psychometric construct evaluation for an assessment session."""

    evaluation_set_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    scenario_id: str = ""
    evaluation_version: str = "1.0.0"
    construct_evaluations: List[ConstructEvaluation] = field(default_factory=list)
    assessments: List[ConstructAssessment] = field(default_factory=list)
    evidence_summaries: List[ConstructEvidenceSummary] = field(default_factory=list)
    evaluation_metadata: Dict[str, Any] = field(default_factory=dict)
    schema_version: str = "1.0.0"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
