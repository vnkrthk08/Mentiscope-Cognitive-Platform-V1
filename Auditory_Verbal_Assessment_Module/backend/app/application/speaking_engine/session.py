from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional
from app.domain.entities.speaking_prompt import SpeakingPrompt
from app.domain.entities.candidate_response import SpeakingResponse


@dataclass
class SpeakingSession:
    """Represents one complete active speaking assessment execution state."""

    session_id: str
    scenario_id: str
    prompts: List[SpeakingPrompt]
    current_prompt_index: int = 0
    recording_status: str = "INITIALIZED"
    responses: Dict[str, SpeakingResponse] = field(default_factory=dict)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    metadata: Dict[str, str] = field(default_factory=dict)

    @property
    def current_prompt(self) -> Optional[SpeakingPrompt]:
        if 0 <= self.current_prompt_index < len(self.prompts):
            return self.prompts[self.current_prompt_index]
        return None

    @property
    def is_completed(self) -> bool:
        return len(self.responses) == len(self.prompts)
