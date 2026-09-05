from typing import List, Optional
from app.domain.entities.speaking_prompt import SpeakingPrompt
from app.domain.exceptions.speaking_exceptions import PromptNotFound


class SpeakingNavigator:
    """Manages speaking prompt sequence navigation."""

    def __init__(self, prompts: List[SpeakingPrompt]):
        self.prompts = prompts
        self.current_index: int = 0

    def get_current_prompt(self) -> SpeakingPrompt:
        if not self.prompts:
            raise PromptNotFound("NONE", "EMPTY_MODULE")
        return self.prompts[self.current_index]

    def has_next(self) -> bool:
        return self.current_index + 1 < len(self.prompts)

    def next_prompt(self) -> Optional[SpeakingPrompt]:
        if self.has_next():
            self.current_index += 1
            return self.get_current_prompt()
        return None
