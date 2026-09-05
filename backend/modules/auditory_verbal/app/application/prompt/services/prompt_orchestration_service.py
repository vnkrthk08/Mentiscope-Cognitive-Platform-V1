import uuid
from datetime import datetime, timezone
from typing import Tuple, Dict, Any
from fastapi import HTTPException, status
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.domain.prompt.entities.prompt_execution import PromptExecution
from app.domain.prompt.entities.prompt_response import PromptResponse
from app.domain.prompt.value_objects.provider_result import ProviderResult
from app.domain.prompt.value_objects.token_usage import TokenUsage
from app.domain.prompt.value_objects.prompt_metadata import PromptMetadata
from app.infrastructure.prompt.template_engine import template_engine
from app.infrastructure.prompt.context_assembler import ContextAssembler
from app.infrastructure.prompt.strategies.provider_selection import LLMSelectionStrategy
from app.infrastructure.prompt.circuit_breaker import llm_breaker_pool
from app.infrastructure.prompt.retry_policy import execute_with_retry
from app.infrastructure.prompt.response_normalizer import LLMResponseNormalizer
from app.infrastructure.prompt.metrics import prompt_metrics, PromptMetric
from app.infrastructure.prompt.orm_models import PromptMetricORM
from app.application.prompt.events import prompt_events


class PromptOrchestrationService:
    """Orchestrates structured LLM prompt context assemblies and execution triggers."""

    @classmethod
    async def execute_prompt(
        cls, transcript_id: str, selection_policy: str, candidate_id: str
    ) -> str:
        # 1. Fetch transcript and validate candidate ownership
        async with UnitOfWork() as uow:
            transcript = await uow.speech_transcripts.get_by_id(transcript_id)
            if not transcript:
                raise HTTPException(status_code=404, detail="Speech transcript not found.")
            if transcript.candidate_id != candidate_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Unauthorized candidate transcript ownership.",
                )

        # 2. Assemble deterministic prompt context variables
        variables = await ContextAssembler.assemble_context(transcript_id)
        
        # Render template
        template_id = "default-assessment-template"
        rendered_prompt = template_engine.render(template_id, variables)

        # 3. Apply provider selection strategy
        provider_name, provider_inst = LLMSelectionStrategy.resolve_provider(selection_policy)

        # Initiate PromptExecution Aggregate
        execution_id = str(uuid.uuid4())
        execution = PromptExecution(
            execution_id=execution_id,
            transcript_id=transcript_id,
            prompt_template=template_id,
            prompt_version="1.0.0",
            assembled_context=rendered_prompt,
            status="PENDING",
        )

        async with UnitOfWork() as uow:
            await uow.llm_prompts.save(execution)
            await uow.commit()

        # Update status to EXECUTING
        execution.start()
        async with UnitOfWork() as uow:
            await uow.llm_prompts.save(execution)
            await uow.commit()

        breaker = llm_breaker_pool.get(provider_name, llm_breaker_pool["openai"])
        start_time = datetime.now(timezone.utc)

        try:
            # 4. Invoke LLM wrap execution in circuit-breaker and retry policies
            async def call_llm() -> Dict[str, Any]:
                return await provider_inst.generate(
                    system_prompt="You are an expert psychometrician extracting candidate behavioral evidence indicators.",
                    user_prompt=rendered_prompt,
                )

            async def call_with_breaker() -> Dict[str, Any]:
                return await breaker.execute(call_llm)

            raw_response = await execute_with_retry(call_with_breaker, max_retries=3)

            # 5. Normalize response and save
            content, input_tok, output_tok = LLMResponseNormalizer.normalize(provider_name, raw_response)
            end_time = datetime.now(timezone.utc)
            duration_ms = float((end_time - start_time).total_seconds() * 1000)

            # Estimate cost
            model_name = raw_response.get("model", "default-model")
            cost = provider_inst.estimate_cost(model_name, input_tok, output_tok)

            # Hydrate values
            result = ProviderResult(
                provider_name=provider_name,
                provider_version="1.0.0",
                model_name=model_name,
                request_id=raw_response.get("id", str(uuid.uuid4())),
                processing_time_ms=duration_ms,
                api_latency_ms=raw_response.get("latency_ms", 100.0),
                estimated_cost_usd=cost,
                raw_metadata=raw_response,
            )

            resp_id = str(uuid.uuid4())
            response = PromptResponse(
                response_id=resp_id,
                execution_id=execution_id,
                content_raw=json.dumps(raw_response),
                content_normalized=content,
            )

            usage = TokenUsage(
                input_tokens=input_tok,
                output_tokens=output_tok,
                total_tokens=input_tok + output_tok,
                estimated_cost_usd=cost,
            )

            meta = PromptMetadata(
                normalization_version="1.0.0",
                pipeline_version="1.0.0",
            )

            execution.complete(result, response, usage, meta)

            async with UnitOfWork() as uow:
                await uow.llm_prompts.save(execution)

                # Persist metrics
                metric_orm = PromptMetricORM(
                    id=uuid.uuid4(),
                    provider_name=provider_name,
                    model_name=model_name,
                    latency_ms=duration_ms,
                    success=True,
                    input_tokens=input_tok,
                    output_tokens=output_tok,
                    estimated_cost_usd=cost,
                )
                await uow.llm_prompts.save_metric(metric_orm)
                await uow.commit()

            return execution_id

        except Exception as e:
            execution.fail()
            async with UnitOfWork() as uow:
                await uow.llm_prompts.save(execution)
                metric_orm = PromptMetricORM(
                    id=uuid.uuid4(),
                    provider_name=provider_name,
                    model_name="unknown",
                    latency_ms=0.0,
                    success=False,
                    input_tokens=0,
                    output_tokens=0,
                    estimated_cost_usd=0.0,
                )
                await uow.llm_prompts.save_metric(metric_orm)
                await uow.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Prompt pipeline execution failed: {str(e)}",
            )


import json
