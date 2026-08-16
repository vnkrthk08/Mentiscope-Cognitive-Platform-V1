from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.modules.gv.answer_service import submit_answer
from backend.modules.gv.item_service import InvalidResponseError, ItemNotFoundError
from backend.modules.gv.result_service import (
    IncompleteAssessmentError,
    ResultNotFoundError,
    finish_assessment,
    get_result,
)
from backend.modules.gv.schemas import (
    AnswerRequest,
    AnswerResponse,
    FinalResult,
    FinishRequest,
    StartRequest,
    StartResponse,
)
from backend.modules.gv.session_service import (
    SessionConflictError,
    SessionStateError,
    require_active_session,
    start_or_resume,
)

router = APIRouter()


@router.post("/start", response_model=StartResponse)
def start(payload: StartRequest, db: Session = Depends(get_db)) -> StartResponse:
    try:
        return start_or_resume(db, payload)
    except SessionConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except SessionStateError as exc:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail=str(exc)) from exc


@router.post("/answer", response_model=AnswerResponse)
def answer(payload: AnswerRequest, db: Session = Depends(get_db)) -> AnswerResponse:
    try:
        session = require_active_session(db, payload.session_id)
        return submit_answer(db, session, payload)
    except SessionStateError as exc:
        code = status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_409_CONFLICT
        raise HTTPException(status_code=code, detail=str(exc)) from exc
    except ItemNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (InvalidResponseError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc


@router.post("/finish", response_model=FinalResult)
def finish(payload: FinishRequest, db: Session = Depends(get_db)) -> FinalResult:
    try:
        # Idempotency: a completed session is retrieved without requiring it to
        # be active again.
        try:
            return get_result(db, payload.session_id, record_view=False)
        except ResultNotFoundError:
            pass
        session = require_active_session(db, payload.session_id)
        return finish_assessment(db, session, payload)
    except IncompleteAssessmentError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except SessionStateError as exc:
        code = status.HTTP_404_NOT_FOUND if "not found" in str(exc).lower() else status.HTTP_409_CONFLICT
        raise HTTPException(status_code=code, detail=str(exc)) from exc
    except ResultNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc


@router.get("/result/{session_id}", response_model=FinalResult)
def result(session_id: str, db: Session = Depends(get_db)) -> FinalResult:
    try:
        return get_result(db, session_id, record_view=True)
    except ResultNotFoundError as exc:
        detail = str(exc)
        code = status.HTTP_404_NOT_FOUND if "not found" in detail.lower() else status.HTTP_409_CONFLICT
        raise HTTPException(status_code=code, detail=detail) from exc
