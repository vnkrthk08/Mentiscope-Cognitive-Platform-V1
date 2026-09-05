from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict
from app.domain.assessment.entities.framework_result import FrameworkResult
from app.domain.assessment.value_objects.scoring_metadata import ScoringMetadata


@dataclass
class AssessmentResult:
    """Domain Entity representing calculated raw and normalized scores across all frameworks."""

    result_id: str
    candidate_id: str
    assessment_id: str
    construct_evaluation_id: str
    framework_results: List[FrameworkResult]
    overall_scores: Dict[str, float]
    overall_confidence: float
    scoring_metadata: ScoringMetadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if not self.result_id or not self.result_id.strip():
            raise ValueError("AssessmentResult result_id cannot be empty.")
        if not self.candidate_id or not self.candidate_id.strip():
            raise ValueError("AssessmentResult candidate_id cannot be empty.")
        if not self.assessment_id or not self.assessment_id.strip():
            raise ValueError("AssessmentResult assessment_id cannot be empty.")
        if not self.construct_evaluation_id or not self.construct_evaluation_id.strip():
            raise ValueError("AssessmentResult construct_evaluation_id cannot be empty.")
        if not self.framework_results:
            raise ValueError("AssessmentResult framework_results cannot be empty.")
        if not (0.0 <= self.overall_confidence <= 1.0):
            raise ValueError("AssessmentResult overall_confidence must range between 0.0 and 1.0.")
pre=1.0
