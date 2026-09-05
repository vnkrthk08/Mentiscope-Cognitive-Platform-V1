"""Assessment Analytics Domain Model."""
from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class TrendPoint:
    date: str
    count: int
    completion_rate: float


@dataclass
class AssessmentAnalytics:
    total_assessments: int = 0
    completed_assessments: int = 0
    in_progress_assessments: int = 0
    overall_completion_rate: float = 0.0
    by_scenario: Dict[str, int] = field(default_factory=dict)
    trend_series: List[TrendPoint] = field(default_factory=list)
