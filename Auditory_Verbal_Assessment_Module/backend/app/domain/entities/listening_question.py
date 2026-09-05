from dataclasses import dataclass, field
from typing import List
from app.domain.value_objects.enums import ConstructType, DifficultyLevel


@dataclass
class ListeningQuestion:
    """Entity representing a deterministic Listening Question item."""

    question_id: str
    prompt: str
    options: List[str]
    correct_option_index: int
    target_construct: ConstructType
    difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    points: int = 10
    max_replays: int = 2
    secondary_constructs: List[ConstructType] = field(default_factory=list)
    question_type: str = "Detail"
    cognitive_objective: str = ""
    expected_evidence: dict = field(default_factory=dict)
    weight: float = 1.0

    def __post_init__(self):
        if not self.question_id or not self.question_id.strip():
            raise ValueError("ListeningQuestion ID cannot be empty.")
        if not self.prompt or not self.prompt.strip():
            raise ValueError("ListeningQuestion prompt text cannot be empty.")
        if len(self.options) < 2:
            raise ValueError("ListeningQuestion must contain at least 2 options.")
        if not (0 <= self.correct_option_index < len(self.options)):
            raise ValueError(
                f"correct_option_index {self.correct_option_index} out of bounds for options count {len(self.options)}."
            )
        if self.points <= 0:
            raise ValueError("ListeningQuestion points must be positive.")
        if self.max_replays < 0:
            raise ValueError("ListeningQuestion max_replays cannot be negative.")
