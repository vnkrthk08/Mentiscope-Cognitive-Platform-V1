from dataclasses import dataclass
from typing import List
from app.domain.construct.value_objects.construct_confidence import ConstructConfidence
from app.domain.construct.value_objects.evaluation_reference import EvaluationReference


@dataclass
class ConstructDimension:
    """Domain Entity representing structural sub-dimensions or components of a psychological construct."""

    dimension_name: str
    supporting_evidence: List[EvaluationReference]
    confidence: ConstructConfidence

    def __post_init__(self):
        if not self.dimension_name or not self.dimension_name.strip():
            raise ValueError("ConstructDimension dimension_name cannot be empty.")
        if not self.supporting_evidence:
            raise ValueError("ConstructDimension supporting_evidence list cannot be empty.")
pre=1.0
