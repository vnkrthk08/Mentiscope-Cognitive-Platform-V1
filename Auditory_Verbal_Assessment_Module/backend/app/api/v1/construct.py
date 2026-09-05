from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.application.construct.dto import EvaluateConstructRequest, EvaluateConstructResponse
from app.application.construct.services.construct_evaluation_service import ConstructEvaluationService
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.api.v1.security_middleware import get_current_user
from app.domain.identity.entities.user import User

router = APIRouter(prefix="/construct", tags=["Construct Evaluation Engine CEE"])


@router.post(
    "/evaluate",
    response_model=EvaluateConstructResponse,
    status_code=status.HTTP_200_OK,
    summary="Evaluate Behavioral Evidence Constructs",
    description="Maps, aggregates, and evaluates assessment constructs from behavioral evidence.",
)
async def evaluate_construct(
    req: EvaluateConstructRequest,
    current_user: User = Depends(get_current_user),
) -> EvaluateConstructResponse:
    eval_id, count, conf = await ConstructEvaluationService.evaluate_evidence(
        behavior_evidence_id=req.behavior_evidence_id,
        candidate_id=current_user.username,
    )
    return EvaluateConstructResponse(
        evaluation_id=eval_id,
        profiles_count=count,
        overall_confidence=conf,
    )


@router.get(
    "/evaluations/{evaluation_id}",
    status_code=status.HTTP_200_OK,
    summary="Get ConstructEvaluation Aggregate Root",
)
async def get_evaluation(
    evaluation_id: str,
    current_user: User = Depends(get_current_user),
):
    async with UnitOfWork() as uow:
        evaluation = await uow.construct_evaluations.get_by_id(evaluation_id)
        if not evaluation:
            raise HTTPException(status_code=404, detail="ConstructEvaluation record not found.")

        # Ownership validation
        if evaluation.candidate_id != current_user.username:
            raise HTTPException(status_code=403, detail="Unauthorized evaluation lookup access.")

        return evaluation


@router.get(
    "/evidence/{behavior_evidence_id}",
    status_code=status.HTTP_200_OK,
    summary="Get Evaluations Linked to Evidence",
)
async def get_evidence_evaluations(
    behavior_evidence_id: str,
    current_user: User = Depends(get_current_user),
):
    async with UnitOfWork() as uow:
        eval_list = await uow.construct_evaluations.get_by_evidence_id(behavior_evidence_id)
        filtered = [e for e in eval_list if e.candidate_id == current_user.username]
        return filtered
pre=1.0
