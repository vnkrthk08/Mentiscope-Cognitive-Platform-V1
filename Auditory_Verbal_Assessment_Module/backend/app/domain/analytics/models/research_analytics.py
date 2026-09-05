"""Research Analytics Domain Model."""
from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class ReviewerWorkload:
    reviewer_id: str
    reviewer_name: str
    completed_reviews: int
    approved_reviews: int
    rejected_reviews: int


@dataclass
class ResearchAnalytics:
    total_validation_datasets: int = 0
    ready_datasets: int = 0
    total_expert_reviews: int = 0
    approved_reviews: int = 0
    total_calibration_batches: int = 0
    completed_calibration_batches: int = 0
    total_exports: int = 0
    exports_by_format: Dict[str, int] = field(default_factory=dict)
    reviewer_workloads: List[ReviewerWorkload] = field(default_factory=list)
