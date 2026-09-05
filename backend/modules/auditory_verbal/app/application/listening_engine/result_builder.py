from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Any
from app.domain.entities.listening_question import ListeningQuestion
from app.domain.entities.candidate_response import ListeningResponse
from app.application.listening_engine.validator import ListeningValidator


@dataclass
class ListeningSessionResult:
    """Result object summarizing listening assessment execution statistics and deterministic accuracy."""

    session_id: str
    scenario_id: str
    total_questions: int
    correct_count: int
    raw_accuracy_percentage: float
    total_response_time_ms: int
    average_response_time_ms: float
    replays_used: Dict[str, int]
    responses: Dict[str, Dict[str, Any]]
    completed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class ListeningResultBuilder:
    """Builds deterministic ListeningSessionResult summary (Does NOT perform scoring!)."""

    def __init__(self):
        self.validator = ListeningValidator()

    def build_result(
        self,
        session_id: str,
        scenario_id: str,
        questions: List[ListeningQuestion],
        responses: Dict[str, ListeningResponse],
        replay_status: Dict[str, int],
    ) -> ListeningSessionResult:
        total_questions = len(questions)
        correct_count = 0
        total_time_ms = 0
        response_summaries: Dict[str, Dict[str, Any]] = {}

        for q in questions:
            resp = responses.get(q.question_id)
            if resp:
                is_correct = self.validator.is_answer_correct(q, resp)
                if is_correct:
                    correct_count += 1
                total_time_ms += resp.response_time_ms

                response_summaries[q.question_id] = {
                    "selected_option_index": resp.selected_option_index,
                    "correct_option_index": q.correct_option_index,
                    "is_correct": is_correct,
                    "response_time_ms": resp.response_time_ms,
                    "target_construct": q.target_construct.value,
                }

        accuracy = round((correct_count / float(total_questions)) * 100.0, 1) if total_questions > 0 else 0.0
        avg_time = round(total_time_ms / float(total_questions), 1) if total_questions > 0 else 0.0

        return ListeningSessionResult(
            session_id=session_id,
            scenario_id=scenario_id,
            total_questions=total_questions,
            correct_count=correct_count,
            raw_accuracy_percentage=accuracy,
            total_response_time_ms=total_time_ms,
            average_response_time_ms=avg_time,
            replays_used=replay_status,
            responses=response_summaries,
        )
