from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import uuid


@dataclass(frozen=True)
class ConstructScore:
    construct: str
    raw_score: float
    normalized_score: float
    weight: float = 1.0
    confidence: float = 0.95
    calibration_version: str = "1.0.0"
    norm_version: str = "1.0.0"


@dataclass(frozen=True)
class CompositeScore:
    composite_name: str
    score: float
    calculation_method: str = "WEIGHTED_AVERAGE"
    supporting_constructs: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class ReliabilitySummary:
    reliability_estimate: float = 0.92
    confidence_interval: str = "0.88 - 0.96"
    internal_consistency: float = 0.89
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AssessmentDecision:
    decision_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    decision_band: str = "HIGH_COMPETENCY"
    decision_explanation: str = "Candidate consistently demonstrated structured problem solving, risk assessment, and clear communication."
    risk_flags: List[str] = field(default_factory=list)
    decision_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class AssessmentScoreSet:
    """Immutable aggregate root representing full psychometric score and decision results."""

    score_set_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    scenario_id: str = ""
    construct_scores: Dict[str, ConstructScore] = field(default_factory=dict)
    composite_scores: Dict[str, CompositeScore] = field(default_factory=dict)
    assessment_decision: Optional[AssessmentDecision] = None
    reliability_summary: Optional[ReliabilitySummary] = None
    scoring_metadata: Dict[str, Any] = field(default_factory=dict)
    pipeline_version: str = "1.0.0"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
