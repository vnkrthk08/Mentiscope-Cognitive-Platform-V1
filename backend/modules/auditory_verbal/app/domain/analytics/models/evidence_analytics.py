"""Evidence Analytics Domain Model."""
from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class ObservationFrequency:
    construct_name: str
    count: int
    avg_confidence: float


@dataclass
class EvidenceAnalytics:
    total_evidence_count: int = 0
    average_quality_score: float = 0.0
    evidence_utilization_rate: float = 0.0
    top_observation_frequencies: List[ObservationFrequency] = field(default_factory=list)
    quality_by_evidence_type: Dict[str, float] = field(default_factory=dict)
