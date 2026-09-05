from typing import List, Dict, Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.persistence.models.orm_models import PromptAuditORM
from app.infrastructure.prompt_service.repository import PromptRepository as InMemoryPromptRepository


class PromptRepository(InMemoryPromptRepository):
    """SQLAlchemy-backed prompt repository managing audit logging and template lookups."""

    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def save_audit_log(
        self,
        prompt_id: str,
        session_id: str,
        template_text: str,
        rendered_text: str,
        prompt_hash: str,
        model_parameters: Dict[str, Any],
        response_payload: Dict[str, Any],
        latency_ms: int,
    ) -> PromptAuditORM:
        orm = PromptAuditORM(
            prompt_id=prompt_id,
            session_id=session_id,
            template_text=template_text,
            rendered_text=rendered_text,
            prompt_hash=prompt_hash,
            model_parameters=model_parameters,
            response_payload=response_payload,
            latency_ms=latency_ms,
        )
        self.session.add(orm)
        await self.session.flush()
        return orm

    async def get_audit_logs_by_session_id(self, session_id: str) -> List[PromptAuditORM]:
        result = await self.session.execute(
            select(PromptAuditORM).where(
                PromptAuditORM.session_id == session_id, PromptAuditORM.is_deleted == False
            )
        )
        return list(result.scalars().all())
