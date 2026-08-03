"""Thread-safe behavioral event logging for assessment interactions."""

from __future__ import annotations

from datetime import UTC, datetime
from threading import RLock
from time import monotonic_ns
from typing import Any, Mapping

from models import DifficultyLevel, EventType, InteractionEvent


class EventLogger:
    """Record immutable events and calculate reaction times server-side."""

    def __init__(self, assessment_id: str, participant_id: str) -> None:
        if not assessment_id.strip() or not participant_id.strip():
            raise ValueError("assessment_id and participant_id are required")
        self.assessment_id, self.participant_id = assessment_id, participant_id
        self._events: list[InteractionEvent] = []
        self._question_starts: dict[str, int] = {}
        self._lock = RLock()

    @property
    def events(self) -> tuple[InteractionEvent, ...]:
        with self._lock:
            return tuple(self._events)

    def record(
        self, event_type: EventType, *, puzzle_id: str | None = None,
        question_id: str | None = None, option_id: str | None = None,
        previous_option_id: str | None = None,
        difficulty: DifficultyLevel | None = None, is_correct: bool | None = None,
        payload: Mapping[str, Any] | None = None,
    ) -> InteractionEvent:
        """Create and append one event using an aware UTC timestamp."""

        with self._lock:
            now_ns = monotonic_ns()
            if event_type is EventType.QUESTION_STARTED and question_id:
                self._question_starts[question_id] = now_ns
            started = self._question_starts.get(question_id or "")
            reaction = int((now_ns - started) / 1_000_000) if started is not None else None
            event = InteractionEvent(
                event_type, self.assessment_id, self.participant_id, puzzle_id,
                question_id, option_id, previous_option_id, reaction, difficulty,
                is_correct, payload or {}, datetime.now(UTC),
            )
            self._events.append(event)
            return event

    def question_started(self, puzzle_id: str, question_id: str, difficulty: DifficultyLevel) -> InteractionEvent:
        return self.record(EventType.QUESTION_STARTED, puzzle_id=puzzle_id, question_id=question_id, difficulty=difficulty)

    def option_selected(self, puzzle_id: str, question_id: str, option_id: str, previous_option_id: str | None = None) -> InteractionEvent:
        event_type = EventType.OPTION_CHANGED if previous_option_id else EventType.OPTION_CLICKED
        return self.record(event_type, puzzle_id=puzzle_id, question_id=question_id, option_id=option_id, previous_option_id=previous_option_id)

    def submitted(self, puzzle_id: str, question_id: str, option_id: str, is_correct: bool, difficulty: DifficultyLevel) -> InteractionEvent:
        return self.record(EventType.ANSWER_SUBMITTED, puzzle_id=puzzle_id, question_id=question_id, option_id=option_id, is_correct=is_correct, difficulty=difficulty)


__all__ = ["EventLogger"]
