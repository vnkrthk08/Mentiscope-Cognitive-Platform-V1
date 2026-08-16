from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.modules.gv.config import MODULE_CONFIG
from backend.modules.gv.event_service import log_server_event, persist_client_events
from backend.modules.gv.item_bank.items import build_item_bank
from backend.modules.gv.models import GvAnswer, GvResult, GvSession
from backend.modules.gv.schemas import FinalResult, FinishRequest
from backend.modules.gv.scoring import compute_metrics


class IncompleteAssessmentError(ValueError):
    pass


class ResultNotFoundError(ValueError):
    pass


def _expected_scored_count(session: GvSession) -> int:
    bank = build_item_bank(session.session_id, session.difficulty)
    return sum(1 for records in bank.values() for record in records if not record.safe["practice"])


def finish_assessment(db: Session, session: GvSession, payload: FinishRequest) -> FinalResult:
    existing = db.get(GvResult, session.session_id)
    if existing is not None:
        return FinalResult.model_validate(existing.payload)

    persist_client_events(db, session, payload.events)
    answer_count = db.scalar(
        select(func.count()).select_from(GvAnswer).where(
            GvAnswer.session_id == session.session_id,
            GvAnswer.practice.is_(False),
        )
    )
    expected = _expected_scored_count(session)
    if int(answer_count or 0) != expected:
        raise IncompleteAssessmentError(
            f"Assessment is incomplete: {answer_count or 0} of {expected} scored items answered"
        )

    end_time = datetime.utcnow()
    session.end_time = end_time
    session.status = "completed"
    session.current_item_index = expected
    log_server_event(db, session, "assessment_finished")
    db.flush()
    metrics = compute_metrics(db, session)
    result = FinalResult(
        student_id=session.student_id,
        session_id=session.session_id,
        module_id=MODULE_CONFIG.module_id,
        module_name=MODULE_CONFIG.module_name,
        construct=MODULE_CONFIG.construct,
        status="Completed",
        start_time=session.start_time,
        end_time=end_time,
        completion_time=max(0.0, (end_time - session.start_time).total_seconds()),
        timestamp=end_time,
        metrics=metrics,
    )
    row = GvResult(
        session_id=session.session_id,
        student_id=session.student_id,
        module_id=MODULE_CONFIG.module_id,
        score_percentage=metrics.raw_score,
        payload=result.model_dump(mode="json"),
    )
    db.add(row)
    db.commit()
    return result


def get_result(db: Session, session_id: str, *, record_view: bool = True) -> FinalResult:
    session = db.get(GvSession, session_id)
    if session is None:
        raise ResultNotFoundError("Gv session not found")
    if session.status != "completed":
        raise ResultNotFoundError(f"Gv result is unavailable because the session is {session.status}")
    result = db.get(GvResult, session_id)
    if result is None:
        raise ResultNotFoundError("Gv result record not found")
    if record_view:
        log_server_event(db, session, "result_viewed")
        db.commit()
    return FinalResult.model_validate(result.payload)
