from dataclasses import dataclass, field
from typing import List, Dict, Any
from app.domain.value_objects.enums import ConstructType


@dataclass
class Construct:
    """Entity representing a psychological/cognitive construct."""

    construct_id: str
    key: ConstructType
    name: str
    description: str
    indicators: List[str]
    rubric_reference_id: str
    relationships: Dict[str, str] = field(default_factory=dict)
    validation_rules: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.construct_id or not self.construct_id.strip():
            raise ValueError("Construct ID cannot be empty.")
        if not self.name or not self.name.strip():
            raise ValueError("Construct name cannot be empty.")
        if not self.description or not self.description.strip():
            raise ValueError("Construct description cannot be empty.")
        if not self.indicators:
            raise ValueError("Construct must contain at least one observable behavioral indicator.")
        if not self.rubric_reference_id or not self.rubric_reference_id.strip():
            raise ValueError("Construct rubric_reference_id cannot be empty.")
