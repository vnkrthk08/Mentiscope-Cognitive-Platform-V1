from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.modules.gv.config import MODULE_CONFIG
from backend.modules.gv.event_service import log_server_event
from backend.modules.gv.item_service import get_safe_sequence
from backend.modules.gv.models import GvAnswer, GvResult, GvSession
from backend.modules.gv.schemas import StartRequest, StartResponse


class SessionConflictError(ValueError):
    pass


class SessionStateError(ValueError):
    pass


def _is_expired(session: GvSession, now: datetime) -> bool:
    return session.status == "expired" or (session.status == "ongoing" and session.expires_at <= now)


def start_or_resume(db: Session, payload: StartRequest) -> StartResponse:
    now = datetime.utcnow()
    session = db.get(GvSession, payload.session_id)
    status = "new"
    if session is not None:
        if session.student_id != payload.student_id:
            raise SessionConflictError("The session belongs to a different student")
        if session.module_id != payload.module_id or session.construct != payload.construct:
            raise SessionConflictError("Session module metadata does not match the Gv module")
        if _is_expired(session, now):
            session.status = "expired"
            session.last_activity_at = now
            db.commit()
            raise SessionStateError("The Gv assessment session has expired")
        if session.status == "abandoned":
            raise SessionStateError("The Gv assessment session was abandoned")
        if session.status == "completed":
            result = db.get(GvResult, session.session_id)
            return StartResponse(
                status="completed",
                student_id=session.student_id,
                session_id=session.session_id,
                module_id=session.module_id,
                module_name=session.module_name,
                construct=session.construct,
                version=MODULE_CONFIG.version,
                difficulty=session.difficulty,
                start_time=session.start_time,
                current_item_index=session.current_item_index,
                practice_items=[],
                assessment_items=[],
                completed_result=result.payload if result else None,
            )
        status = "resumed"
    else:
        practice, scored = get_safe_sequence(payload.session_id, payload.difficulty)
        session = GvSession(
            session_id=payload.session_id,
            student_id=payload.student_id,
            module_id=payload.module_id,
            module_name=MODULE_CONFIG.module_name,
            construct=payload.construct,
            difficulty=payload.difficulty,
            status="ongoing",
            current_item_index=0,
            start_time=now,
            last_activity_at=now,
            expires_at=now + timedelta(hours=MODULE_CONFIG.session_expiry_hours),
            item_order=[item["item_id"] for item in scored],
            session_metadata={"module_version": MODULE_CONFIG.version},
        )
        try:
            db.add(session)
            db.flush()
            log_server_event(db, session, "session_started", response={"difficulty": payload.difficulty})
            db.commit()
            db.refresh(session)
        except IntegrityError:
            db.rollback()
            session = db.get(GvSession, payload.session_id)
            if session is None:
                raise
            status = "resumed"

    session.last_activity_at = now
    practice_items, assessment_items = get_safe_sequence(session.session_id, session.difficulty)
    answered = {
        row[0]
        for row in db.execute(
            select(GvAnswer.item_id).where(
                GvAnswer.session_id == session.session_id,
                GvAnswer.practice.is_(False),
            )
        ).all()
    }
    current_index = 0
    for index, item_id in enumerate(session.item_order):
        if item_id not in answered:
            current_index = index
            break
    else:
        current_index = len(session.item_order)
    session.current_item_index = current_index
    db.commit()
    return StartResponse(
        status=status,
        student_id=session.student_id,
        session_id=session.session_id,
        module_id=session.module_id,
        module_name=session.module_name,
        construct=session.construct,
        version=MODULE_CONFIG.version,
        difficulty=session.difficulty,
        start_time=session.start_time,
        current_item_index=current_index,
        practice_items=practice_items,
        assessment_items=assessment_items,
        completed_result=None,
    )


def require_active_session(db: Session, session_id: str) -> GvSession:
    session = db.get(GvSession, session_id)
    if session is None:
        raise SessionStateError("Gv session not found")
    now = datetime.utcnow()
    if _is_expired(session, now):
        session.status = "expired"
        db.commit()
        raise SessionStateError("The Gv assessment session has expired")
    if session.status != "ongoing":
        raise SessionStateError(f"Gv session is {session.status}")
    session.last_activity_at = now
    return session
