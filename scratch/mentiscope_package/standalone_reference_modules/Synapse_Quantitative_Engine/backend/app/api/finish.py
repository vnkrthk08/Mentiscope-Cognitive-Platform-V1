from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.database.database import get_db
from app.services.finish_service import FinishService
from app.schemas.finish import FinishRequest

router = APIRouter(
    prefix="/api",
    tags=["Assessment"],
)

@router.post("/finish")
def finish(
    request: FinishRequest,
    db: Session = Depends(get_db),
):
    return FinishService.finish(
        db,
        request,
    )