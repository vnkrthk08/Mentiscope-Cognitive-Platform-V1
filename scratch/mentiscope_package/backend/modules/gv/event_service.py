from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from backend.modules.gv.config import MODULE_CONFIG
from backend.modules.gv.models import GvEvent, GvSession
from backend.modules.gv.schemas import ClientEvent


def _increment_metadata(session: GvSession, key: str, amount: int = 1) -> None:
    metadata = dict(session.session_metadata or {})
    metadata[key] = int(metadata.get(key, 0)) + amount
    session.session_metadata = metadata


def log_server_event(
    db: Session,
    session: GvSession,
    event_type: str,
    *,
    subtest_id: str | None = None,
    item_id: str | None = None,
    response: dict | None = None,
    correct: bool | None = None,
    time_taken: float = 0,
) -> GvEvent:
    event = GvEvent(
        event_id=f"GV-SERVER-{uuid4().hex}",
        student_id=session.student_id,
        session_id=session.session_id,
        module_id=MODULE_CONFIG.module_id,
        subtest_id=subtest_id,
        item_id=item_id,
        event_type=event_type,
        response=response or {},
        correct=correct,
        time_taken=max(0.0, float(time_taken)),
        time_since_session_start=max(0.0, (datetime.utcnow() - session.start_time).total_seconds()),
        attempt_number=1,
        difficulty_level=session.difficulty,
        timestamp=datetime.utcnow(),
    )
    db.add(event)
    return event


def persist_client_events(db: Session, session: GvSession, events: list[ClientEvent]) -> tuple[int, int]:
    inserted = 0
    duplicates = 0
    for payload in events:
        if payload.session_id != session.session_id or payload.student_id != session.student_id:
            _increment_metadata(session, "rejected_event_count")
            continue
        if payload.module_id != MODULE_CONFIG.module_id:
            _increment_metadata(session, "rejected_event_count")
            continue
        if db.get(GvEvent, payload.event_id) is not None:
            duplicates += 1
            continue
        # Client correctness is never used as authoritative scoring. It is
        # retained only for practice or non-scored interaction interpretation.
        event = GvEvent(
            event_id=payload.event_id,
            student_id=payload.student_id,
            session_id=payload.session_id,
            module_id=payload.module_id,
            subtest_id=payload.subtest_id,
            item_id=payload.item_id,
            event_type=payload.event_type,
            response=payload.response,
            correct=payload.correct,
            time_taken=payload.time_taken,
            time_since_session_start=payload.time_since_session_start,
            attempt_number=payload.attempt_number,
            difficulty_level=payload.difficulty_level,
            timestamp=payload.timestamp,
        )
        db.add(event)
        inserted += 1
    if duplicates:
        _increment_metadata(session, "duplicate_event_count", duplicates)
    _increment_metadata(session, "received_event_count", len(events))
    return inserted, duplicates
