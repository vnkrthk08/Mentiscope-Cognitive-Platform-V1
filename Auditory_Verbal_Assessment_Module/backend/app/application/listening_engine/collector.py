from app.domain.entities.candidate_response import ListeningResponse
from app.domain.entities.listening_question import ListeningQuestion
from app.domain.exceptions.listening_exceptions import InvalidAnswerOption


class ListeningResponseCollector:
    """Captures candidate answers and constructs immutable ListeningResponse domain entities."""

    def collect_response(
        self,
        session_id: str,
        question: ListeningQuestion,
        selected_option_index: int,
        response_time_ms: int,
    ) -> ListeningResponse:
        if not (0 <= selected_option_index < len(question.options)):
            raise InvalidAnswerOption(question.question_id, selected_option_index, len(question.options))

        return ListeningResponse(
            session_id=session_id,
            prompt_id=question.question_id,
            selected_option_index=selected_option_index,
            response_time_ms=response_time_ms,
        )
