from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from modules.quantitative.database.database import get_db
from modules.quantitative.services.finish_service import FinishService
from modules.quantitative.schemas.finish import FinishRequest

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