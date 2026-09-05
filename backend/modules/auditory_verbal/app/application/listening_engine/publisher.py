from app.core.event_bus import event_bus
from app.domain.events.listening_events import (
    AudioStarted,
    ReplayRequested,
    ReplayCompleted,
    QuestionPresented,
    AnswerSubmitted,
    ListeningCancelled,
    ListeningFailed,
)
from app.domain.events.assessment_events import ListeningStarted, ListeningCompleted


class ListeningEventPublisher:
    """Helper for publishing deterministic listening domain events to the Event Bus."""

    async def publish_started(self, session_id: str, total_questions: int):
        await event_bus.publish("ListeningStarted", ListeningStarted(session_id=session_id, total_questions=total_questions))

    async def publish_audio_started(self, session_id: str, audio_url: str, duration_sec: float):
        await event_bus.publish("AudioStarted", AudioStarted(session_id=session_id, audio_url=audio_url, duration_seconds=duration_sec))

    async def publish_replay_requested(self, session_id: str, item_id: str, replay_num: int):
        await event_bus.publish("ReplayRequested", ReplayRequested(session_id=session_id, item_id=item_id, requested_replay_number=replay_num))

    async def publish_replay_completed(self, session_id: str, item_id: str, remaining_replays: int):
        await event_bus.publish("ReplayCompleted", ReplayCompleted(session_id=session_id, item_id=item_id, remaining_replays=remaining_replays))

    async def publish_question_presented(self, session_id: str, qid: str, idx: int, total: int):
        await event_bus.publish("QuestionPresented", QuestionPresented(session_id=session_id, question_id=qid, question_index=idx, total_questions=total))

    async def publish_answer_submitted(self, session_id: str, qid: str, selected_idx: int, is_correct: bool, time_ms: int):
        await event_bus.publish("AnswerSubmitted", AnswerSubmitted(session_id=session_id, question_id=qid, selected_option_index=selected_idx, is_correct=is_correct, response_time_ms=time_ms))

    async def publish_completed(self, session_id: str, questions_count: int, correct_count: int):
        await event_bus.publish("ListeningCompleted", ListeningCompleted(session_id=session_id, questions_count=questions_count, correct_answers_count=correct_count))

    async def publish_cancelled(self, session_id: str, reason: str):
        await event_bus.publish("ListeningCancelled", ListeningCancelled(session_id=session_id, reason=reason))

    async def publish_failed(self, session_id: str, reason: str):
        await event_bus.publish("ListeningFailed", ListeningFailed(session_id=session_id, reason=reason))
