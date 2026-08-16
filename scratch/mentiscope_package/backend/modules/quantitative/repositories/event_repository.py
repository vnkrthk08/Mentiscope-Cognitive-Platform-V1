from sqlalchemy.orm import Session

from modules.quantitative.models.event_log import EventLog


class EventRepository:

    @staticmethod
    def create(
        db: Session,
        event: EventLog,
    ):

        db.add(event)

        db.commit()

        db.refresh(event)

        return event