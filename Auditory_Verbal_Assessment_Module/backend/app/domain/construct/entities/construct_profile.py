from dataclasses import dataclass
from typing import List
from app.domain.construct.value_objects.construct_confidence import ConstructConfidence
from app.domain.construct.value_objects.evaluation_reference import EvaluationReference


@dataclass
class ConstructProfile:
    """Domain Entity mapping candidate performance indicators against a specific construct model framework."""

    framework: str  # CHC, RIASEC, PERSONALITY, EMOTIONAL_REGULATION
    construct_name: str
    supporting_observations: List[EvaluationReference]
    confidence: ConstructConfidence
    evaluation_summary: str

    def __post_init__(self):
        if not self.framework or not self.framework.strip():
            raise ValueError("ConstructProfile framework cannot be empty.")
        if not self.construct_name or not self.construct_name.strip():
            raise ValueError("ConstructProfile construct_name cannot be empty.")
        if not self.supporting_observations:
            raise ValueError("ConstructProfile supporting_observations list cannot be empty.")
        if not self.evaluation_summary or not self.evaluation_summary.strip():
            raise ValueError("ConstructProfile evaluation_summary text cannot be empty.")
pre=1.0
