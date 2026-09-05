"""Framework Analytics Domain Model."""
from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class FrameworkMetrics:
    framework_name: str
    average_score: float = 0.0
    average_confidence: float = 0.0
    coverage_rate: float = 0.0
    total_evaluations: int = 0
    score_distribution: Dict[str, int] = field(default_factory=dict)  # e.g. {"0-20": 5, "21-40": 12...}


@dataclass
class FrameworkAnalytics:
    chc: FrameworkMetrics = field(default_factory=lambda: FrameworkMetrics(framework_name="CHC"))
    riasec: FrameworkMetrics = field(default_factory=lambda: FrameworkMetrics(framework_name="RIASEC"))
    personality: FrameworkMetrics = field(default_factory=lambda: FrameworkMetrics(framework_name="Personality"))
    emotional_regulation: FrameworkMetrics = field(default_factory=lambda: FrameworkMetrics(framework_name="Emotional Regulation"))
    all_frameworks: List[FrameworkMetrics] = field(default_factory=list)
