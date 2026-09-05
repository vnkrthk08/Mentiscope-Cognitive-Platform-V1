from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Any
from app.domain.entities.metric import Metric
from app.domain.entities.evidence import Evidence


@dataclass
class AssessmentReport:
    """Aggregate Root representing the final assessment report payload."""

    report_id: str
    session_id: str
    candidate_id: str
    scenario_id: str
    overall_cognitive_index: float
    listening_metrics: List[Metric]
    speaking_metrics: List[Metric]
    construct_scores: Dict[str, float]
    evidence_summary: List[Evidence]
    recommendations: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if not self.report_id or not self.report_id.strip():
            raise ValueError("AssessmentReport report_id cannot be empty.")
        if not self.session_id or not self.session_id.strip():
            raise ValueError("AssessmentReport session_id cannot be empty.")
        if not self.candidate_id or not self.candidate_id.strip():
            raise ValueError("AssessmentReport candidate_id cannot be empty.")
        if not (0.0 <= self.overall_cognitive_index <= 100.0):
            raise ValueError("AssessmentReport overall_cognitive_index must be between 0.0 and 100.0.")
