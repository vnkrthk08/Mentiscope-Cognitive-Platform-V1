from datetime import datetime

from sqlalchemy.orm import Session

from core_models import AnalyticsRecord, EventRecord, ResponseRecord, ResultRecord, SessionRecord

MODULE_ID = "csr"


class CsrRepository:
    """Persists Classroom Scenario Recall (CSR) activity into the shared
    sessions/responses/events/results/analytics tables. No module-specific
    table is introduced, per the platform's single-shared-schema requirement."""

    def __init__(self, db: Session):
        self.db = db

    def ensure_session(self, session_id: str, student_id: str | None) -> SessionRecord:
        record = self.db.get(SessionRecord, session_id)
        if record is None:
            record = SessionRecord(session_id=session_id, student_id=student_id or "unknown", module_id=MODULE_ID)
            self.db.add(record)
            try:
                self.db.commit()
            except Exception:
                self.db.rollback()
                record = self.db.get(SessionRecord, session_id)
        else:
            self.db.commit()
        return record

    def record_answer(self, session_id: str, item_id: str, answer: str, correct: bool, duration_ms: int, difficulty: int) -> None:
        self.db.add(ResponseRecord(session_id=session_id, item_id=item_id, response=answer, correct=correct, reaction_time_ms=duration_ms, difficulty_level=difficulty))
        self.db.add(EventRecord(session_id=session_id, event_type="selection", payload={"item_id": item_id, "correct": correct, "reaction_time_ms": duration_ms}))
        self.db.commit()

    def responses(self, session_id: str) -> list[ResponseRecord]:
        return self.db.query(ResponseRecord).filter_by(session_id=session_id).all()

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
