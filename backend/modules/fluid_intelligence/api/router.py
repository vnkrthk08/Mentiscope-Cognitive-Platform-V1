from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.modules.fluid_intelligence.repositories.assessment_repository import FluidIntelligenceRepository
from backend.modules.fluid_intelligence.schemas import AnswerRequest, FinishRequest, StartRequest
from backend.modules.fluid_intelligence.services.assessment_service import FluidIntelligenceAssessmentService

router = APIRouter()

def service(db: Session = Depends(get_db)) -> FluidIntelligenceAssessmentService:
    return FluidIntelligenceAssessmentService(FluidIntelligenceRepository(db))

@router.post("/start")
def start(payload: StartRequest, assessment: FluidIntelligenceAssessmentService = Depends(service)):
    return assessment.start(payload.session_id, payload.student_id)

@router.post("/answer")
def answer(payload: AnswerRequest, assessment: FluidIntelligenceAssessmentService = Depends(service)):
    return assessment.answer(payload.session_id, payload.question_id, payload.answer, payload.duration_ms)

@router.post("/finish")
def finish(payload: FinishRequest, assessment: FluidIntelligenceAssessmentService = Depends(service)):
    return assessment.finish(payload.session_id)

@router.get("/result")
def result(session_id: str, assessment: FluidIntelligenceAssessmentService = Depends(service)):
    return assessment.result(session_id)

@router.get("/result/student/{student_id}")
def result_for_student(student_id: str, assessment: FluidIntelligenceAssessmentService = Depends(service)):
    return assessment.result_for_student(student_id)


