"""
==========================================================
Event Service
==========================================================
"""

from app.models.event_log import EventLog
from app.repositories.event_repository import EventRepository


class EventService:

    @staticmethod
    def log_event(
        db,
        student_id,
        session_id,
        construct,
        task_id,
        item_id,
        event_type,
        response,
        correct,
        reaction_time_ms,
        difficulty_level,
        hint_used=False,
        error_type=None,
    ):

        event = EventLog(

            student_id=student_id,

            session_id=session_id,

            construct=construct,

            task_id=task_id,

            item_id=item_id,

            event_type=event_type,

            response=response,

            correct=correct,

            reaction_time_ms=reaction_time_ms,

            error_type=error_type,

            difficulty_level=difficulty_level,

            event_metadata={
                "hint_used": hint_used
            }
        )

        return EventRepository.create(
            db,
            event,
        )