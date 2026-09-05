from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List
from app.domain.assessment.entities.framework_result import FrameworkResult
from app.domain.assessment.entities.assessment_summary import AssessmentSummary
from app.domain.assessment.value_objects.report_metadata import ReportMetadata


@dataclass
class AssessmentReport:
    """Aggregate Root representing final explainable candidate assessment report."""

    report_id: str
    assessment_result_id: str
    candidate_id: str
    assessment_id: str
    assessment_summary: AssessmentSummary
    framework_results: List[FrameworkResult]
    report_metadata: ReportMetadata
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if not self.report_id or not self.report_id.strip():
            raise ValueError("AssessmentReport report_id cannot be empty.")
        if not self.assessment_result_id or not self.assessment_result_id.strip():
            raise ValueError("AssessmentReport assessment_result_id cannot be empty.")
        if not self.candidate_id or not self.candidate_id.strip():
            raise ValueError("AssessmentReport candidate_id cannot be empty.")
        if not self.assessment_id or not self.assessment_id.strip():
            raise ValueError("AssessmentReport assessment_id cannot be empty.")
        if not self.framework_results:
            raise ValueError("AssessmentReport framework_results cannot be empty.")
pre=1.0
