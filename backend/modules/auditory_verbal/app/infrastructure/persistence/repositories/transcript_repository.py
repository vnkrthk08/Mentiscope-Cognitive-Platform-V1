from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.persistence.models.orm_models import TranscriptORM


class TranscriptRepository:
    """SQLAlchemy repository for candidate speaking responses transcript records."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(
        self, session_id: str, prompt_id: str, transcript_text: str, confidence_score: float = 1.0
    ) -> TranscriptORM:
        orm = TranscriptORM(
            session_id=session_id,
            prompt_id=prompt_id,
            transcript_text=transcript_text,
            confidence_score=confidence_score,
        )
        self.session.add(orm)
        await self.session.flush()
        return orm

    async def get_by_session_id(self, session_id: str) -> List[TranscriptORM]:
        result = await self.session.execute(
            select(TranscriptORM).where(
                TranscriptORM.session_id == session_id, TranscriptORM.is_deleted == False
            )
        )
        return list(result.scalars().all())
