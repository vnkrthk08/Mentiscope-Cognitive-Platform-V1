from typing import List, Optional
from app.domain.entities.listening_question import ListeningQuestion
from app.domain.exceptions.listening_exceptions import QuestionNotFound


class ListeningNavigator:
    """Manages question sequence navigation and progress tracking."""

    def __init__(self, questions: List[ListeningQuestion]):
        self.questions = questions
        self.current_index: int = 0

    def get_current_question(self) -> ListeningQuestion:
        if not self.questions:
            raise QuestionNotFound("NONE", "EMPTY_MODULE")
        return self.questions[self.current_index]

    def has_next(self) -> bool:
        return self.current_index + 1 < len(self.questions)

    def next_question(self) -> Optional[ListeningQuestion]:
        if self.has_next():
            self.current_index += 1
            return self.get_current_question()
        return None
