"""
ASAT â€“ MentiScope Standard Assessment Endpoints

These are the NEW endpoints required by the MentiScope platform specification:
  - POST /api/start
  - POST /api/answer
  - POST /api/finish
  - GET  /api/result/{session_id}

They coexist alongside the existing endpoints for backward compatibility.
The existing frontend continues to use the original endpoints.
The MentiScope platform will use these standardized endpoints.
"""

import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from modules.gsm.database import get_db
from modules.gsm.config import settings
from modules.gsm.schemas import Session as SessionModel, Score, Event, Student
from modules.gsm.models import (
    AssessmentStartRequest, AssessmentStartResponse,
    AssessmentAnswerRequest, AssessmentAnswerResponse,
    AssessmentFinishRequest, AssessmentResultResponse,
    AssessmentMetrics, MessageResponse,
)

logger = logging.getLogger("asat.assessment")
router = APIRouter(tags=["MentiScope Assessment"])


@router.post("/start", response_model=AssessmentStartResponse)
async def start_assessment(
    payload: AssessmentStartRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Start an assessment session.
    Called by the MentiScope platform with student/session metadata.
    As specified in Section 4 & 8 of the MentiScope instructions.

    This endpoint:
    1. Receives student_id, session_id from the platform (no personal details)
    2. Creates/finds the student record
    3. Creates a new session
    4. Returns assessment configuration
    """
    now = datetime.now(timezone.utc)

    # Find or create student by platform student_id
    result = await db.execute(
        select(Student).where(Student.student_id_number == payload.student_id)
    )
    student = result.scalar_one_or_none()

    if not student:
        # Create a minimal student record from platform data
        student = Student(
            full_name=f"Student {payload.student_id}",
            student_id_number=payload.student_id,
        )
        db.add(student)
        await db.commit()
        await db.refresh(student)
        logger.info(f"[assessment/start] Created student for platform id={payload.student_id}")

    # Create session with the platform-provided session_id as UUID
    session = SessionModel(
        student_id=student.student_id,
        session_uuid=payload.session_id,
        status="in_progress",
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    logger.info(
        f"[assessment/start] Session created: session_id={session.session_id} "
        f"student_id={payload.student_id} platform_session={payload.session_id}"
    )

    return AssessmentStartResponse(
        status="started",
        session_id=payload.session_id,
        module_id=payload.module_id or settings.module_id,
        module_name=settings.module_name,
        construct=payload.construct or settings.construct,
        total_trials=112,
        modules=["Sustained", "Selective", "Divided", "Executive"],
        start_time=now.isoformat(),
    )


@router.post("/answer", response_model=AssessmentAnswerResponse)
async def submit_answer(
    payload: AssessmentAnswerRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Log a single trial answer/event.
    As specified in Section 7 & 8 of the MentiScope instructions.
    """
    # Find the session by platform session_id (stored as session_uuid)
    result = await db.execute(
        select(SessionModel).where(SessionModel.session_uuid == payload.session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {payload.session_id} not found.")

    # Find the student
    student_result = await db.execute(
        select(Student).where(Student.student_id_number == payload.student_id)
    )
    student = student_result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail=f"Student {payload.student_id} not found.")

    # Log the event â€” same fields as existing event logging
    event = Event(
        student_id=student.student_id,
        session_id=session.session_id,
        construct=settings.construct,
        task_id=payload.task_id or settings.module_name,
        item_id=payload.item_id,
        stimulus=payload.stimulus or "",
        event_type=payload.event_type or "TRIAL",
        response=payload.response or "",
        correct=payload.correct,
        reaction_time_ms=payload.reaction_time_ms or 0,
        error_type=payload.error_type or "",
        difficulty_level=payload.difficulty_level or 1,
    )
    db.add(event)
    await db.commit()

    logger.info(
        f"[assessment/answer] Event logged: session={payload.session_id} "
        f"item={payload.item_id} correct={payload.correct} rt={payload.reaction_time_ms}ms"
    )
    return AssessmentAnswerResponse(status="recorded", item_id=payload.item_id)


@router.post("/finish", response_model=AssessmentResultResponse)
async def finish_assessment(
    payload: AssessmentFinishRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Complete the assessment and return MentiScope-standard results.
    As specified in Sections 5, 6, & 8 of the MentiScope instructions.
    """
    now = datetime.now(timezone.utc)

    # Find session
    result = await db.execute(
        select(SessionModel).where(SessionModel.session_uuid == payload.session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {payload.session_id} not found.")

    # Find student
    student_result = await db.execute(
        select(Student).where(Student.student_id_number == payload.student_id)
    )
    student = student_result.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail=f"Student {payload.student_id} not found.")

    # Mark session completed
    session.status = "completed"
    session.end_time = now

    # Save scores â€” same upsert logic as sessions.py
    if payload.scores:
        score_result = await db.execute(
            select(Score)
            .where(Score.student_id == student.student_id)
            .order_by(desc(Score.created_at))
            .limit(1)
        )
        existing_score = score_result.scalar_one_or_none()

        mr = payload.module_results or {}

        if existing_score:
            existing_score.sustained_score = payload.scores.sustained
            existing_score.selective_score = payload.scores.selective
            existing_score.divided_score = payload.scores.divided
            existing_score.executive_score = payload.scores.executive
            existing_score.overall_score = payload.scores.overall
            existing_score.percentile = payload.scores.percentile or 0
            existing_score.module_results = mr
            existing_score.raw_score = payload.scores.overall
            existing_score.normalized_score = (payload.scores.overall or 0) / 100
            existing_score.sub_scores = {
                "sustained": payload.scores.sustained,
                "selective": payload.scores.selective,
                "divided": payload.scores.divided,
                "executive": payload.scores.executive,
            }
            existing_score.confidence_score = 0.95
        else:
            new_score = Score(
                student_id=student.student_id,
                sustained_score=payload.scores.sustained,
                selective_score=payload.scores.selective,
                divided_score=payload.scores.divided,
                executive_score=payload.scores.executive,
                overall_score=payload.scores.overall,
                percentile=payload.scores.percentile or 0,
                module_results=mr,
                raw_score=payload.scores.overall,
                normalized_score=(payload.scores.overall or 0) / 100,
                sub_scores={
                    "sustained": payload.scores.sustained,
                    "selective": payload.scores.selective,
                    "divided": payload.scores.divided,
                    "executive": payload.scores.executive,
                },
                confidence_score=0.95,
            )
            db.add(new_score)

    await db.commit()

    # Calculate completion time
    completion_time = None
    if session.start_time:
        delta = now - session.start_time.replace(tzinfo=timezone.utc)
        completion_time = int(delta.total_seconds())

    # Extract metrics from module_results for the standard response
    mr = payload.module_results or {}
    sustained_mr = mr.get("sustained", {}) or {}
    selective_mr = mr.get("selective", {}) or {}
    executive_mr = mr.get("executive", {}) or {}

    metrics = AssessmentMetrics(
        sustained_score=payload.scores.sustained if payload.scores else None,
        selective_score=payload.scores.selective if payload.scores else None,
        divided_score=payload.scores.divided if payload.scores else None,
        executive_score=payload.scores.executive if payload.scores else None,
        overall_score=payload.scores.overall if payload.scores else None,
        percentile=payload.scores.percentile if payload.scores else None,
        rt_variability=sustained_mr.get("rtVariabilityScore"),
        fatigue_slope=sustained_mr.get("fatigueScore"),
        adaptation_speed=executive_mr.get("adaptationSpeed"),
        impulsivity_index=sustained_mr.get("impulsivityIndex"),
        attention_stability=sustained_mr.get("attentionStability"),
        recovery_after_errors=sustained_mr.get("recoveryTrials"),
    )

    logger.info(
        f"[assessment/finish] Assessment completed: session={payload.session_id} "
        f"overall={payload.scores.overall if payload.scores else 'N/A'}"
    )

    return AssessmentResultResponse(
        student_id=payload.student_id,
        session_id=payload.session_id,
        module_id=settings.module_id,
        module_name=settings.module_name,
        construct=settings.construct,
        status="Completed",
        start_time=session.start_time.isoformat() if session.start_time else None,
        end_time=now.isoformat(),
        completion_time=completion_time,
        timestamp=now.isoformat(),
        metrics=metrics,
    )


@router.get("/result/{session_id}", response_model=AssessmentResultResponse)
async def get_result(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve assessment results by session ID.
    As specified in Section 8 of the MentiScope instructions.
    Returns the standard output format with mandatory metadata + metrics.
    """
    # Find session by UUID
    result = await db.execute(
        select(SessionModel).where(SessionModel.session_uuid == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found.")

    # Get student
    student_result = await db.execute(
        select(Student).where(Student.student_id == session.student_id)
    )
    student = student_result.scalar_one_or_none()

    # Get latest score
    score_result = await db.execute(
        select(Score)
        .where(Score.student_id == session.student_id)
        .order_by(desc(Score.created_at))
        .limit(1)
    )
    score = score_result.scalar_one_or_none()

    # Calculate completion time
    completion_time = None
    if session.start_time and session.end_time:
        delta = session.end_time - session.start_time
        completion_time = int(delta.total_seconds())

    # Extract metrics from module_results
    mr = score.module_results if score and score.module_results else {}
    sustained_mr = mr.get("sustained", {}) or {}
    executive_mr = mr.get("executive", {}) or {}

    metrics = AssessmentMetrics(
        sustained_score=score.sustained_score if score else None,
        selective_score=score.selective_score if score else None,
        divided_score=score.divided_score if score else None,
        executive_score=score.executive_score if score else None,
        overall_score=score.overall_score if score else None,
        percentile=score.percentile if score else None,
        rt_variability=sustained_mr.get("rtVariabilityScore"),
        fatigue_slope=sustained_mr.get("fatigueScore"),
        adaptation_speed=executive_mr.get("adaptationSpeed"),
        impulsivity_index=sustained_mr.get("impulsivityIndex"),
        attention_stability=sustained_mr.get("attentionStability"),
        recovery_after_errors=sustained_mr.get("recoveryTrials"),
    )

    return AssessmentResultResponse(
        student_id=student.student_id_number or str(student.student_id) if student else "unknown",
        session_id=session_id,
        module_id=settings.module_id,
        module_name=settings.module_name,
        construct=settings.construct,
        status=session.status or "unknown",
        start_time=session.start_time.isoformat() if session.start_time else None,
        end_time=session.end_time.isoformat() if session.end_time else None,
        completion_time=completion_time,
        timestamp=session.end_time.isoformat() if session.end_time else None,
        metrics=metrics,
    )
