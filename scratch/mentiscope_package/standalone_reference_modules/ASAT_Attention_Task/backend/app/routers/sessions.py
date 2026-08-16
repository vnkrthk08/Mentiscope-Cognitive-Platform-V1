"""
ASAT – Session & Score Routes

Translated from: backend/routes/sessions.js
Same business logic: session creation, score upsert, batch event logging.
"""

import logging
from uuid import uuid4
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func

from app.database import get_db
from app.schemas import Session as SessionModel, Score, Event
from app.models import (
    SessionCreateRequest, SessionCreateResponse,
    SessionUpdateRequest, EventsBatchRequest,
    MessageResponse,
)

logger = logging.getLogger("asat.sessions")
router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


@router.post("", response_model=SessionCreateResponse, status_code=201)
async def create_session(
    payload: SessionCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Create assessment session.
    Translated from: POST /api/sessions in sessions.js
    """
    if not payload.studentId:
        raise HTTPException(status_code=400, detail="studentId required.")

    uuid = str(uuid4())
    session = SessionModel(
        student_id=payload.studentId,
        session_uuid=uuid,
        status="in_progress",
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    logger.info(
        f"[sessions/create] INSERT sessions student_id={payload.studentId} "
        f"session_id={session.session_id} uuid={uuid}"
    )
    return SessionCreateResponse(sessionId=session.session_id, sessionUuid=uuid)


@router.patch("/{session_id}", response_model=MessageResponse)
async def update_session(
    session_id: int,
    payload: SessionUpdateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Update session with final scores.
    Translated from: PATCH /api/sessions/:id in sessions.js
    Same upsert logic for scores table.
    """
    logger.info(f"[sessions/patch] Updating session_id={session_id} student_id={payload.studentId}")

    if not payload.studentId:
        raise HTTPException(status_code=400, detail="studentId is required in request body.")

    # Mark session completed — same SQL as original
    result = await db.execute(
        select(SessionModel).where(SessionModel.session_id == session_id)
    )
    session = result.scalar_one_or_none()
    if session:
        session.status = "completed"
        session.end_time = func.now()

    # Upsert scores — same logic as original
    if payload.scores:
        score_result = await db.execute(
            select(Score)
            .where(Score.student_id == payload.studentId)
            .order_by(desc(Score.created_at))
            .limit(1)
        )
        existing = score_result.scalar_one_or_none()

        mr_json = payload.moduleResults or {}
        raw_score = payload.scores.overall
        normalized_score = (payload.scores.overall or 0) / 100
        percentile = payload.scores.percentile or 0
        sub_scores = {
            "sustained": payload.scores.sustained,
            "selective": payload.scores.selective,
            "divided": payload.scores.divided,
            "executive": payload.scores.executive,
        }
        confidence_score = 0.95

        if existing:
            # UPDATE — same as original
            existing.sustained_score = payload.scores.sustained
            existing.selective_score = payload.scores.selective
            existing.divided_score = payload.scores.divided
            existing.executive_score = payload.scores.executive
            existing.overall_score = payload.scores.overall
            existing.percentile = percentile
            existing.module_results = mr_json
            existing.raw_score = raw_score
            existing.normalized_score = normalized_score
            existing.sub_scores = sub_scores
            existing.confidence_score = confidence_score
            logger.info(
                f"[sessions/patch] UPDATE scores score_id={existing.score_id} "
                f"student_id={payload.studentId}"
            )
        else:
            # INSERT — same as original
            new_score = Score(
                student_id=payload.studentId,
                sustained_score=payload.scores.sustained,
                selective_score=payload.scores.selective,
                divided_score=payload.scores.divided,
                executive_score=payload.scores.executive,
                overall_score=payload.scores.overall,
                percentile=percentile,
                module_results=mr_json,
                raw_score=raw_score,
                normalized_score=normalized_score,
                sub_scores=sub_scores,
                confidence_score=confidence_score,
            )
            db.add(new_score)
            logger.info(f"[sessions/patch] INSERT scores for student_id={payload.studentId}")

        logger.info(
            f"[sessions/patch] Scores: sustained={payload.scores.sustained} "
            f"selective={payload.scores.selective} divided={payload.scores.divided} "
            f"executive={payload.scores.executive} overall={payload.scores.overall}"
        )

    await db.commit()
    logger.info(f"[sessions/patch] Done. Session {session_id} marked completed.")
    return MessageResponse(message="Session updated.")


@router.post("/{session_id}/modules", response_model=MessageResponse)
async def save_module_result(session_id: int):
    """
    Save a single module result (lightweight).
    Translated from: POST /api/sessions/:id/modules in sessions.js
    """
    # Original was also lightweight — actual score save happens at PATCH
    return MessageResponse(message="Module noted.")


@router.post("/{session_id}/events", response_model=MessageResponse)
async def save_events(
    session_id: int,
    payload: EventsBatchRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Batch save trial events.
    Translated from: POST /api/sessions/:id/events in sessions.js
    Same bulk insert logic.
    """
    if not payload.events:
        raise HTTPException(status_code=400, detail="No events provided")

    # Bulk insert — same fields as original
    event_objects = [
        Event(
            student_id=payload.studentId,
            session_id=session_id,
            construct=e.construct or "Attention",
            task_id=e.taskId or "ASAT",
            item_id=e.itemId or 0,
            stimulus=e.stimulus or "",
            event_type=e.eventType or "TRIAL",
            response=e.response or "",
            correct=bool(e.correct),
            reaction_time_ms=e.reactionTimeMs or 0,
            error_type=e.errorType or "",
            difficulty_level=e.difficultyLevel or 1,
        )
        for e in payload.events
    ]

    db.add_all(event_objects)
    await db.commit()

    logger.info(f"[sessions/events] {len(payload.events)} events logged for session {session_id}")
    return MessageResponse(message=f"{len(payload.events)} events logged successfully.")
