from fastapi import APIRouter, Depends, HTTPException, status
from app.application.speech.dto import TranscribeRequest, TranscribeResponse, JobStatusResponse
from app.application.speech.services.speech_processing_service import SpeechProcessingService
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.api.v1.security_middleware import get_current_user
from app.domain.identity.entities.user import User

router = APIRouter(prefix="/speech", tags=["Speech processing STT"])


@router.post(
    "/transcribe",
    response_model=TranscribeResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger Audio Transcription",
    description="Starts asynchronous speech transcription for a validated audio asset.",
)
async def trigger_transcription(
    req: TranscribeRequest,
    current_user: User = Depends(get_current_user),
) -> TranscribeResponse:
    job_id, _ = await SpeechProcessingService.create_transcription_job(
        asset_id=req.asset_id,
        selection_policy=req.selection_policy,
        candidate_id=current_user.username,
    )
    return TranscribeResponse(job_id=job_id, status="PENDING")


@router.get(
    "/jobs/{job_id}",
    response_model=JobStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Transcription Job Status",
)
async def get_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
) -> JobStatusResponse:
    async with UnitOfWork() as uow:
        job = await uow.transcription_jobs.get_by_id(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Transcription job not found.")

        # Ownership validation through the asset candidate identity
        asset = await uow.audio_assets.get_by_id(job.asset_id)
        if not asset or asset.candidate_id != current_user.username:
            raise HTTPException(status_code=403, detail="Unauthorized job lookup access.")

        return JobStatusResponse(
            job_id=job.job_id,
            asset_id=job.asset_id,
            provider=job.provider,
            status=job.status,
            retry_count=job.retry_count,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
        )


@router.get(
    "/transcripts/{transcript_id}",
    status_code=status.HTTP_200_OK,
    summary="Get persited Transcript Aggregate Root",
)
async def get_transcript(
    transcript_id: str,
    current_user: User = Depends(get_current_user),
):
    async with UnitOfWork() as uow:
        transcript = await uow.speech_transcripts.get_by_id(transcript_id)
        if not transcript:
            raise HTTPException(status_code=404, detail="Transcript record not found.")

        # Validate candidate ownership
        if transcript.candidate_id != current_user.username:
            raise HTTPException(status_code=403, detail="Unauthorized transcript access.")

        return transcript
