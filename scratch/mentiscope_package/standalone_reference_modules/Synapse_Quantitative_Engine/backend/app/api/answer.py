"""
==========================================================
Answer API
==========================================================
"""

from fastapi import APIRouter

from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db

from app.schemas.answer import (
    AnswerRequest,
    AnswerResponse,
)

from app.services.answer_service import AnswerService

router = APIRouter(
    prefix="/api",
    tags=["Assessment"],
)


@router.post(
    "/answer",
    response_model=AnswerResponse,
)
def submit_answer(
    request: AnswerRequest,
    db: Session = Depends(get_db),
):

    result = AnswerService.submit_answer(
        db,
        request,
    )

    return AnswerResponse(**result)