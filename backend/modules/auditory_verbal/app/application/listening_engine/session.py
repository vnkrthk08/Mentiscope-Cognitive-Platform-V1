from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional
from app.domain.entities.listening_question import ListeningQuestion
from app.domain.entities.candidate_response import ListeningResponse


@dataclass
class ListeningSession:
    """Represents one complete active listening assessment execution state."""

    session_id: str
    scenario_id: str
    audio_id: str
    questions: List[ListeningQuestion]
    current_question_index: int = 0
    replay_status: Dict[str, int] = field(default_factory=dict)
    responses: Dict[str, ListeningResponse] = field(default_factory=dict)
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    status: str = "INITIALIZED"

    @property
    def current_question(self) -> Optional[ListeningQuestion]:
        if 0 <= self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None

    @property
    def is_completed(self) -> bool:
        return len(self.responses) == len(self.questions)
