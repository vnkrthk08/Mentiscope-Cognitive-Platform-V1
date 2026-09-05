from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from app.domain.entities.behavioural_indicator import BehaviouralIndicator
from app.domain.value_objects.enums import ConstructType
from app.domain.value_objects.time_limit import TimeLimit


@dataclass
class SpeakingPrompt:
    """Entity representing a Speaking Task prompt with canonical psychometric configuration."""

    prompt_id: str
    title: str
    instructions: str
    time_limit: TimeLimit = field(default_factory=lambda: TimeLimit(max_seconds=120))
    question_id: str = "SQ1"
    stage: str = "STAGE_1_DECISION"
    objective: str = ""
    primary_constructs: List[ConstructType] = field(default_factory=list)
    secondary_constructs: List[ConstructType] = field(default_factory=list)
    behavioural_indicators: List[BehaviouralIndicator] = field(default_factory=list)
    max_indicator_weighted_score: float = 18.4
    followup_eligible: bool = True

    def __init__(
        self,
        prompt_id: str,
        title: str,
        instructions: str,
        time_limit: Optional[TimeLimit] = None,
        question_id: str = "SQ1",
        stage: str = "STAGE_1_DECISION",
        objective: str = "",
        primary_constructs: Optional[List[ConstructType]] = None,
        secondary_constructs: Optional[List[ConstructType]] = None,
        behavioural_indicators: Optional[List[BehaviouralIndicator]] = None,
        max_indicator_weighted_score: float = 18.4,
        followup_eligible: bool = True,
        target_constructs: Optional[List[ConstructType]] = None,
    ):
        self.prompt_id = prompt_id
        self.title = title
        self.instructions = instructions
        self.time_limit = time_limit or TimeLimit(max_seconds=120)
        self.question_id = question_id
        self.stage = stage
        self.objective = objective
        self.max_indicator_weighted_score = max_indicator_weighted_score
        self.followup_eligible = followup_eligible
        self.behavioural_indicators = behavioural_indicators or []

        # Handle primary and secondary constructs with backward-compatibility for target_constructs
        if primary_constructs is not None or secondary_constructs is not None:
            self.primary_constructs = primary_constructs or []
            self.secondary_constructs = secondary_constructs or []
        elif target_constructs is not None:
            # Infer primary vs secondary if target_constructs was passed
            if target_constructs:
                self.primary_constructs = [target_constructs[0]]
                self.secondary_constructs = target_constructs[1:] if len(target_constructs) > 1 else []
            else:
                self.primary_constructs = []
                self.secondary_constructs = []
        else:
            self.primary_constructs = []
            self.secondary_constructs = []

        self._validate_invariants()

    def _validate_invariants(self):
        if not self.prompt_id or not self.prompt_id.strip():
            raise ValueError("SpeakingPrompt ID cannot be empty.")
        if not self.title or not self.title.strip():
            raise ValueError("SpeakingPrompt title cannot be empty.")
        if not self.instructions or not self.instructions.strip():
            raise ValueError("SpeakingPrompt instructions cannot be empty.")
        if not self.primary_constructs and not self.secondary_constructs:
            raise ValueError("SpeakingPrompt must evaluate at least one target construct.")

    @property
    def target_constructs(self) -> List[ConstructType]:
        """Backward compatibility property returning combined list of unique constructs."""
        combined = []
        for c in self.primary_constructs + self.secondary_constructs:
            if c not in combined:
                combined.append(c)
        return combined

    @target_constructs.setter
    def target_constructs(self, value: List[ConstructType]):
        if value:
            self.primary_constructs = [value[0]]
            self.secondary_constructs = value[1:] if len(value) > 1 else []
        else:
            self.primary_constructs = []
            self.secondary_constructs = []
