from dataclasses import dataclass, field
from typing import Dict, List, Optional
from app.domain.entities.listening_question import ListeningQuestion
from app.domain.entities.speaking_prompt import SpeakingPrompt
from app.domain.entities.follow_up_question import FollowUpQuestion
from app.domain.value_objects.audio_asset import AudioAsset
from app.domain.value_objects.enums import ConstructType, DifficultyLevel
from app.domain.value_objects.scenario_version import ScenarioVersion


@dataclass
class Scenario:
    """Aggregate Root representing a complete unified assessment scenario."""

    scenario_id: str
    title: str
    narrative: str
    audio_asset: AudioAsset
    listening_questions: List[ListeningQuestion]
    speaking_prompts: List[SpeakingPrompt]
    version: ScenarioVersion
    difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE
    follow_up_definitions: List[FollowUpQuestion] = field(default_factory=list)
    construct_mappings: List[ConstructType] = field(default_factory=list)
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        # Invariant checks
        if not self.scenario_id or not self.scenario_id.strip():
            raise ValueError("Scenario scenario_id cannot be empty.")
        if not self.title or not self.title.strip():
            raise ValueError("Scenario title cannot be empty.")
        if not self.narrative or not self.narrative.strip():
            raise ValueError("Scenario narrative text cannot be empty.")
        if not self.listening_questions:
            raise ValueError("Scenario invariant violation: Scenario must contain at least one listening question.")
        if not self.speaking_prompts:
            raise ValueError("Scenario invariant violation: Scenario must contain at least one speaking prompt.")

    def get_listening_question(self, question_id: str) -> Optional[ListeningQuestion]:
        for q in self.listening_questions:
            if q.question_id == question_id:
                return q
        return None

    def get_speaking_prompt(self, prompt_id: str) -> Optional[SpeakingPrompt]:
        for p in self.speaking_prompts:
            if p.prompt_id == prompt_id:
                return p
        return None
