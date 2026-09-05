from dataclasses import dataclass, field
from typing import Dict, Any
from app.domain.value_objects.scenario_version import ScenarioVersion


@dataclass
class Rubric:
    """Entity representing deterministic scoring rubrics and weights."""

    rubric_id: str
    construct_key: str
    base_weight: float
    positive_indicator_points: float
    negative_indicator_penalty: float
    bands: Dict[str, float]
    formula_reference: str
    version: ScenarioVersion

    def __post_init__(self):
        if not self.rubric_id or not self.rubric_id.strip():
            raise ValueError("Rubric ID cannot be empty.")
        if not self.construct_key or not self.construct_key.strip():
            raise ValueError("Rubric construct_key cannot be empty.")
        if self.base_weight <= 0:
            raise ValueError("Rubric base_weight must be greater than 0.")
        if not self.bands:
            raise ValueError("Rubric invariant violation: Rubric must define at least one scoring band threshold.")
