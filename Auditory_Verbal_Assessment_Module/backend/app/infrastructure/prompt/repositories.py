import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.prompt.entities.prompt_execution import PromptExecution
from app.domain.prompt.entities.prompt_template import PromptTemplate
from app.domain.prompt.entities.prompt_response import PromptResponse
from app.domain.prompt.value_objects.provider_result import ProviderResult
from app.domain.prompt.value_objects.token_usage import TokenUsage
from app.domain.prompt.value_objects.prompt_metadata import PromptMetadata
from app.infrastructure.prompt.orm_models import PromptExecutionORM, PromptTemplateORM, PromptResponseORM, PromptMetricORM


class PromptMapper:
    @staticmethod
    def to_domain(orm: PromptExecutionORM, resp_orm: Optional[PromptResponseORM] = None) -> PromptExecution:
        result_vo = None
        if orm.provider_result:
            p = orm.provider_result
            result_vo = ProviderResult(
                provider_name=p["provider_name"],
                provider_version=p["provider_version"],
                model_name=p["model_name"],
                request_id=p["request_id"],
                processing_time_ms=p["processing_time_ms"],
                api_latency_ms=p["api_latency_ms"],
                estimated_cost_usd=p["estimated_cost_usd"],
                raw_metadata=p.get("raw_metadata", {}),
            )

        usage_vo = None
        if orm.token_usage:
            u = orm.token_usage
            usage_vo = TokenUsage(
                input_tokens=u["input_tokens"],
                output_tokens=u["output_tokens"],
                total_tokens=u["total_tokens"],
                estimated_cost_usd=u["estimated_cost_usd"],
            )

        meta_vo = None
        if orm.execution_metadata:
            m = orm.execution_metadata
            gen_at = datetime.fromisoformat(m["generated_at"]) if isinstance(m["generated_at"], str) else m["generated_at"]
            meta_vo = PromptMetadata(
                normalization_version=m["normalization_version"],
                pipeline_version=m["pipeline_version"],
                generated_at=gen_at,
            )

        resp_vo = None
        if resp_orm:
            resp_vo = PromptResponse(
                response_id=str(resp_orm.id),
                execution_id=str(resp_orm.execution_id),
                content_raw=resp_orm.content_raw,
                content_normalized=resp_orm.content_normalized,
                received_at=resp_orm.received_at,
            )

        return PromptExecution(
            execution_id=str(orm.id),
            transcript_id=str(orm.transcript_id),
            prompt_template=orm.prompt_template,
            prompt_version=orm.prompt_version,
            assembled_context=orm.assembled_context,
            provider_result=result_vo,
            response=resp_vo,
            token_usage=usage_vo,
            execution_metadata=meta_vo,
            status=orm.status,
            created_at=orm.created_at,
            completed_at=orm.completed_at,
        )

    @staticmethod
    def to_orm(domain: PromptExecution) -> PromptExecutionORM:
        res_payload = None
        if domain.provider_result:
            res_payload = {
                "provider_name": domain.provider_result.provider_name,
                "provider_version": domain.provider_result.provider_version,
                "model_name": domain.provider_result.model_name,
                "request_id": domain.provider_result.request_id,
                "processing_time_ms": domain.provider_result.processing_time_ms,
                "api_latency_ms": domain.provider_result.api_latency_ms,
                "estimated_cost_usd": domain.provider_result.estimated_cost_usd,
                "raw_metadata": domain.provider_result.raw_metadata,
            }

        usage_payload = None
        if domain.token_usage:
            usage_payload = {
                "input_tokens": domain.token_usage.input_tokens,
                "output_tokens": domain.token_usage.output_tokens,
                "total_tokens": domain.token_usage.total_tokens,
                "estimated_cost_usd": domain.token_usage.estimated_cost_usd,
            }

        meta_payload = None
        if domain.execution_metadata:
            meta_payload = {
                "normalization_version": domain.execution_metadata.normalization_version,
                "pipeline_version": domain.execution_metadata.pipeline_version,
                "generated_at": domain.execution_metadata.generated_at.isoformat(),
            }

        return PromptExecutionORM(
            id=uuid.UUID(domain.execution_id),
            transcript_id=uuid.UUID(domain.transcript_id),
            prompt_template=domain.prompt_template,
            prompt_version=domain.prompt_version,
            assembled_context=domain.assembled_context,
            provider_result=res_payload,
            token_usage=usage_payload,
            execution_metadata=meta_payload,
            status=domain.status,
            created_at=domain.created_at,
            completed_at=domain.completed_at,
        )


class PromptRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, execution_id: str) -> Optional[PromptExecution]:
        try:
            eid = uuid.UUID(execution_id)
        except ValueError:
            return None
        orm = await self.session.get(PromptExecutionORM, eid)
        if not orm:
            return None
        
        # Load associated response if present
        res = await self.session.execute(
            select(PromptResponseORM).where(PromptResponseORM.execution_id == eid)
        )
        resp_orm = res.scalars().first()
        
        return PromptMapper.to_domain(orm, resp_orm)

    async def save(self, execution: PromptExecution) -> PromptExecution:
        orm = PromptMapper.to_orm(execution)
        existing = await self.session.get(PromptExecutionORM, orm.id)
        if existing:
            existing.status = orm.status
            existing.provider_result = orm.provider_result
            existing.token_usage = orm.token_usage
            existing.execution_metadata = orm.execution_metadata
            existing.completed_at = orm.completed_at
            orm = existing
        else:
            self.session.add(orm)
            
        # Save associated response if complete
        if execution.response:
            resp_orm = PromptResponseORM(
                id=uuid.UUID(execution.response.response_id),
                execution_id=uuid.UUID(execution.response.execution_id),
                content_raw=execution.response.content_raw,
                content_normalized=execution.response.content_normalized,
                received_at=execution.response.received_at,
            )
            existing_resp = await self.session.get(PromptResponseORM, resp_orm.id)
            if not existing_resp:
                self.session.add(resp_orm)

        await self.session.flush()
        
        res = await self.session.execute(
            select(PromptResponseORM).where(PromptResponseORM.execution_id == orm.id)
        )
        resp_orm = res.scalars().first()
        return PromptMapper.to_domain(orm, resp_orm)

    async def save_metric(self, metric_orm: PromptMetricORM) -> None:
        self.session.add(metric_orm)
        await self.session.flush()

    async def list_templates(self) -> List[PromptTemplate]:
        result = await self.session.execute(select(PromptTemplateORM))
        return [
            PromptTemplate(
                template_id=orm.id,
                name=orm.name,
                template_text=orm.template_text,
                version=orm.version,
                required_variables=orm.required_variables.split(",") if orm.required_variables else [],
            )
            for orm in result.scalars().all()
        ]

    async def save_template(self, tpl: PromptTemplate) -> None:
        orm = PromptTemplateORM(
            id=tpl.template_id,
            name=tpl.name,
            template_text=tpl.template_text,
            version=tpl.version,
            required_variables=",".join(tpl.required_variables),
        )
        existing = await self.session.get(PromptTemplateORM, orm.id)
        if not existing:
            self.session.add(orm)
            await self.session.flush()
