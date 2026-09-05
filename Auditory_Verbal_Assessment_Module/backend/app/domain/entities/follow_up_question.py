from dataclasses import dataclass
from typing import Dict, Any
from app.domain.value_objects.enums import ConstructType
from app.domain.value_objects.time_limit import TimeLimit


@dataclass
class FollowUpQuestion:
    """Entity representing an Adaptive Follow-up question item."""

    followup_id: str
    parent_prompt_id: str
    prompt_text: str
    target_construct: ConstructType
    priority: int
    trigger_conditions: Dict[str, Any]
    expected_evidence_pattern: str
    time_limit: TimeLimit = TimeLimit(max_seconds=90)

    def __post_init__(self):
        if not self.followup_id or not self.followup_id.strip():
            raise ValueError("FollowUpQuestion ID cannot be empty.")
        if not self.parent_prompt_id or not self.parent_prompt_id.strip():
            raise ValueError("FollowUpQuestion parent_prompt_id cannot be empty.")
        if not self.prompt_text or not self.prompt_text.strip():
            raise ValueError("FollowUpQuestion prompt_text cannot be empty.")
        if self.priority < 1:
            raise ValueError("FollowUpQuestion priority must be >= 1.")
