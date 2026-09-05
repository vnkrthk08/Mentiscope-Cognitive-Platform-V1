from typing import Dict, List
from app.domain.entities.listening_question import ListeningQuestion
from app.domain.entities.candidate_response import ListeningResponse
from app.domain.exceptions.listening_exceptions import ListeningValidationError


class ListeningValidator:
    """Deterministic rule-based answer evaluator for Listening Questions (Zero AI!)."""

    def is_answer_correct(self, question: ListeningQuestion, response: ListeningResponse) -> bool:
        return response.selected_option_index == question.correct_option_index

    def validate_completion(self, questions: List[ListeningQuestion], responses: Dict[str, ListeningResponse]):
        missing = [q.question_id for q in questions if q.question_id not in responses]
        if missing:
            raise ListeningValidationError(f"Missing answers for listening questions: {', '.join(missing)}")
