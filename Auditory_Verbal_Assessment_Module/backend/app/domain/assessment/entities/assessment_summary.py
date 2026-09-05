from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class AssessmentSummary:
    """Domain Entity describing qualitative assessment feedback derived from quantitative scoring structures."""

    framework_overview: Dict[str, str]
    strengths: List[str]
    areas_for_improvement: List[str]
    confidence_summary: str
    overall_observations: str

    def __post_init__(self):
        if not self.confidence_summary or not self.confidence_summary.strip():
            raise ValueError("AssessmentSummary confidence_summary cannot be empty.")
        if not self.overall_observations or not self.overall_observations.strip():
            raise ValueError("AssessmentSummary overall_observations cannot be empty.")
pre=1.0
