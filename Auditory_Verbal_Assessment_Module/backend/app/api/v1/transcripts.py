from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.api.v1.schemas.responses import TranscriptResponse

router = APIRouter(prefix="/sessions", tags=["Transcripts"])


@router.get(
    "/{id}/transcript",
    response_model=List[TranscriptResponse],
    summary="Get Transcripts",
    description="Loads all voice audio transcription records generated during speaking assessment.",
)
async def get_session_transcripts(id: str) -> List[TranscriptResponse]:
    async with UnitOfWork() as uow:
        # Load associated transcripts
        records = await uow.transcripts.get_by_session_id(id)
        if not records:
            # Check if session exists at least
            session = await uow.assessments.get_by_id(id)
            if not session:
                raise HTTPException(status_code=404, detail="Session not found")
            return []

        return [
            TranscriptResponse(
                session_id=t.session_id,
                prompt_id=t.prompt_id,
                transcript_text=t.transcript_text,
                confidence_score=t.confidence_score,
                is_final=t.is_final,
            )
            for t in records
        ]
