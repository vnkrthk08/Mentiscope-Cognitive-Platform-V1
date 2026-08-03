from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.result_service import ResultService

router = APIRouter(
    prefix="/api",
    tags=["Assessment"],
)

@router.get("/result/{assessment_id}")
def result(
    assessment_id: str,
    db: Session = Depends(get_db),
):

    return ResultService.result(
        db,
        assessment_id,
    )