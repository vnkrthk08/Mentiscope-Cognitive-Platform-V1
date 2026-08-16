from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from modules.quantitative.database.database import get_db

from modules.quantitative.schemas.session import (
    SessionStartRequest,
    SessionStartResponse,
)

from modules.quantitative.services.session_service import SessionService

router = APIRouter(
    prefix="/api",
    tags=["Assessment"],
)


@router.post(
    "/start",
    response_model=SessionStartResponse,
)
def start_assessment(
    request: SessionStartRequest,
    db: Session = Depends(get_db),
):

    session, question = SessionService.create_session(
        db,
        request,
    )

    return SessionStartResponse(

        assessment_id=session.id,

        student_id=session.student_id,

        session_id=session.session_id,

        status=session.status.value,

        started_at=session.started_at,

        question=question
    )