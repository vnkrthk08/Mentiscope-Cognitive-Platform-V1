from datetime import datetime

import sqlalchemy
from sqlalchemy.orm import Session

from backend.core_models import AnalyticsRecord, EventRecord, ResponseRecord, ResultRecord, SessionRecord

MODULE_ID = "gf"

class FluidIntelligenceRepository:
    def __init__(self, db: Session):
        self.db = db

    def ensure_session(self, session_id: str, student_id: str | None) -> SessionRecord:
        record = self.db.get(SessionRecord, session_id)
        if record is None:
            record = SessionRecord(session_id=session_id, student_id=student_id or "unknown", module_id=MODULE_ID)
            self.db.add(record)
            try:
                self.db.commit()
            except sqlalchemy.exc.IntegrityError:
                self.db.rollback()
                record = self.db.get(SessionRecord, session_id)
        return record

    def record_answer(self, session_id: str, item_id: str, answer: str, correct: bool, duration_ms: int, difficulty: str) -> None:
        self.db.add(ResponseRecord(session_id=session_id, item_id=item_id, response=answer, correct=correct, reaction_time_ms=duration_ms, difficulty_level=0))
        self.db.add(EventRecord(session_id=session_id, event_type="selection", payload={"item_id": item_id, "correct": correct, "reaction_time_ms": duration_ms, "difficulty": difficulty}))
        try:
            self.db.commit()
        except sqlalchemy.exc.IntegrityError:
            self.db.rollback()

    def responses(self, session_id: str) -> list[ResponseRecord]:
        return self.db.query(ResponseRecord).filter_by(session_id=session_id).all()

    def events(self, session_id: str) -> list[EventRecord]:
        return self.db.query(EventRecord).filter_by(session_id=session_id).all()

    def save_result(self, session_id: str, score: float, analytics: dict) -> None:
        self.db.query(ResultRecord).filter_by(session_id=session_id).delete()
        self.db.query(AnalyticsRecord).filter_by(session_id=session_id).delete()
        self.db.add(ResultRecord(session_id=session_id, module_id=MODULE_ID, score_percentage=score, payload=analytics))
        self.db.add(AnalyticsRecord(session_id=session_id, module_id=MODULE_ID, payload=analytics))
        session = self.db.get(SessionRecord, session_id)
        if session:
            session.end_time = datetime.utcnow()
        self.db.commit()

    def result(self, session_id: str) -> ResultRecord | None:
        return self.db.query(ResultRecord).filter_by(session_id=session_id, module_id=MODULE_ID).first()

    def result_for_student(self, student_id: str) -> ResultRecord | None:
        return (
            self.db.query(ResultRecord)
            .join(SessionRecord, SessionRecord.session_id == ResultRecord.session_id)
            .filter(SessionRecord.student_id == student_id, ResultRecord.module_id == MODULE_ID)
            .order_by(SessionRecord.start_time.desc())
            .first()
        )


