from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

try:
    from ....database import get_db
except (ImportError, ValueError):
    from database import get_db
from ..repositories import ProcessingSpeedRepository
from ..schemas import AnswerRequest, FinishRequest, StartRequest
from ..services import ProcessingSpeedAssessmentService

router = APIRouter()


def service(db: Session = Depends(get_db)) -> ProcessingSpeedAssessmentService:
    return ProcessingSpeedAssessmentService(ProcessingSpeedRepository(db))


@router.post("/start")
def start(payload: StartRequest, assessment: ProcessingSpeedAssessmentService = Depends(service)):
    return assessment.start(payload.session_id, payload.student_id)


@router.post("/answer")
def answer(payload: AnswerRequest, assessment: ProcessingSpeedAssessmentService = Depends(service)):
    return assessment.answer(payload.session_id, payload.question_id, payload.answer, payload.duration_ms)


@router.post("/finish")
def finish(payload: FinishRequest, assessment: ProcessingSpeedAssessmentService = Depends(service)):
    return assessment.finish(payload.session_id)


@router.get("/result")
def result(session_id: str, assessment: ProcessingSpeedAssessmentService = Depends(service)):
    return assessment.result(session_id)
