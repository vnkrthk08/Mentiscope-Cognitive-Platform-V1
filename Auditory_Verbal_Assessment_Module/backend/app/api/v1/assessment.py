from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.application.assessment.dto import GenerateReportRequest, GenerateReportResponse
from app.application.assessment.services.assessment_scoring_service import AssessmentScoringService
from app.application.assessment.services.assessment_report_service import AssessmentReportService
from app.api.v1.security_middleware import get_current_user
from app.domain.identity.entities.user import User

router = APIRouter(prefix="/assessment", tags=["Assessment Scoring & Report ASR"])


@router.post(
    "/generate",
    response_model=GenerateReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Assessment Report",
    description="Generates qualitative summary reports and explainable psychometric profiles.",
)
async def generate_report(
    req: GenerateReportRequest,
    current_user: User = Depends(get_current_user),
) -> GenerateReportResponse:
    report_id, result_id, conf = await AssessmentScoringService.generate_report(
        construct_evaluation_id=req.construct_evaluation_id,
        candidate_id=current_user.username,
    )
    return GenerateReportResponse(
        report_id=report_id,
        assessment_result_id=result_id,
        overall_confidence=conf,
    )


@router.get(
    "/reports/{report_id}",
    status_code=status.HTTP_200_OK,
    summary="Retrieve Assessment Report",
)
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_user),
):
    report = await AssessmentReportService.get_report(report_id, current_user.username)
    if not report:
        raise HTTPException(status_code=404, detail="AssessmentReport not found or unauthorized.")
    return report


@router.get(
    "/results/{result_id}",
    status_code=status.HTTP_200_OK,
    summary="Retrieve Assessment Result",
)
async def get_result(
    result_id: str,
    current_user: User = Depends(get_current_user),
):
    result = await AssessmentReportService.get_result(result_id, current_user.username)
    if not result:
        raise HTTPException(status_code=404, detail="AssessmentResult not found or unauthorized.")
    return result


@router.get(
    "/candidate/{candidate_id}",
    status_code=status.HTTP_200_OK,
    summary="Retrieve Candidate Reports",
)
async def get_candidate_reports(
    candidate_id: str,
    current_user: User = Depends(get_current_user),
):
    # Enforce candidate self-check lookup constraints
    if current_user.username != candidate_id:
        raise HTTPException(status_code=403, detail="Unauthorized candidate reports lookup access.")
    return await AssessmentReportService.get_candidate_reports(candidate_id)
pre=1.0
