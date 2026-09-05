from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.application.behavior.dto import ExtractEvidenceRequest, ExtractEvidenceResponse
from app.application.behavior.services.behavior_extraction_service import BehaviorExtractionService
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.api.v1.security_middleware import get_current_user
from app.domain.identity.entities.user import User

router = APIRouter(prefix="/behavior", tags=["Behavioral Evidence Extraction BEE"])


@router.post(
    "/extract",
    response_model=ExtractEvidenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Extract Behavioral Evidence",
    description="Starts behavioral evidence extraction from completed prompt responses.",
)
async def extract_behavior(
    req: ExtractEvidenceRequest,
    current_user: User = Depends(get_current_user),
) -> ExtractEvidenceResponse:
    evidence_id, ok, count = await BehaviorExtractionService.extract_behavioral_evidence(
        execution_id=req.prompt_execution_id,
        candidate_id=current_user.username,
    )
    return ExtractEvidenceResponse(
        evidence_id=evidence_id,
        validation_passed=ok,
        observations_count=count,
    )


@router.get(
    "/evidence/{evidence_id}",
    status_code=status.HTTP_200_OK,
    summary="Get BehaviorEvidence Aggregate Root",
)
async def get_evidence(
    evidence_id: str,
    current_user: User = Depends(get_current_user),
):
    async with UnitOfWork() as uow:
        evidence = await uow.behavior_evidences.get_by_id(evidence_id)
        if not evidence:
            raise HTTPException(status_code=404, detail="BehaviorEvidence aggregate not found.")

        # Ownership validation
        if evidence.candidate_id != current_user.username:
            raise HTTPException(status_code=403, detail="Unauthorized evidence lookup access.")

        return evidence


@router.get(
    "/transcript/{transcript_id}",
    status_code=status.HTTP_200_OK,
    summary="Get Evidence Linked to Transcript",
)
async def get_transcript_evidence(
    transcript_id: str,
    current_user: User = Depends(get_current_user),
):
    async with UnitOfWork() as uow:
        evidence_list = await uow.behavior_evidences.get_by_transcript_id(transcript_id)
        # Filter ownership
        filtered = [e for e in evidence_list if e.candidate_id == current_user.username]
        return filtered
