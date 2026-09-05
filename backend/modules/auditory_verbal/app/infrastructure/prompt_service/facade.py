from datetime import datetime, timezone
from typing import Dict, Any, Optional
from app.core.logging import logger
from app.infrastructure.prompt_service.repository import PromptRepository
from app.infrastructure.prompt_service.renderer import PromptRenderer
from app.infrastructure.prompt_service.validator import PromptValidator
from app.infrastructure.prompt_service.router import ModelRouter
from app.infrastructure.prompt_service.response_validator import ResponseValidator
from app.infrastructure.prompt_service.audit_manager import PromptAuditManager
from app.infrastructure.prompt_service.result import PromptOrchestrationResult
from app.infrastructure.prompt_service.publisher import PromptEventPublisher
from app.domain.exceptions.prompt_exceptions import PromptOrchestrationFailure


class AIPromptOrchestrationService:
    """Facade for the AI Prompt Orchestration Service (APOS).
    The EXCLUSIVE gateway for all LLM prompt execution within MentiScope.
    Loads templates, validates required variables, renders prompts, routes models,
    validates structured JSON schemas, records audit trails, and returns PromptOrchestrationResult.
    """

    def __init__(
        self,
        repository: Optional[PromptRepository] = None,
        renderer: Optional[PromptRenderer] = None,
        validator: Optional[PromptValidator] = None,
        router: Optional[ModelRouter] = None,
        response_validator: Optional[ResponseValidator] = None,
        audit_manager: Optional[PromptAuditManager] = None,
        publisher: Optional[PromptEventPublisher] = None,
    ):
        self.repository = repository or PromptRepository()
        self.renderer = renderer or PromptRenderer()
        self.validator = validator or PromptValidator()
        self.router = router or ModelRouter()
        self.response_validator = response_validator or ResponseValidator()
        self.audit_manager = audit_manager or PromptAuditManager()
        self.publisher = publisher or PromptEventPublisher()

    async def execute_prompt(
        self,
        prompt_id: str,
        variables: Dict[str, Any],
        version: str = "1.0.0",
        preferred_model: str = "gemini-1.5-pro",
    ) -> PromptOrchestrationResult:
        """Executes full prompt orchestration pipeline and returns validated JSON output result."""
        import os
        from app.core.config import settings
        from app.infrastructure.prompt.circuit_breaker import llm_breaker_pool
        from app.infrastructure.prompt.retry_policy import execute_with_retry

        logger.info(f"[APOS FACADE] Executing prompt '{prompt_id}' (v{version})")
        start_time = datetime.now(timezone.utc)

        try:
            # 1. Load Template & Validate Required Variables
            template = self.repository.get_template(prompt_id, version)
            await self.publisher.publish_loaded(prompt_id, template.version)

            self.validator.validate_variables(template, variables)

            # 2. Render Template
            rendered_text = self.renderer.render(template, variables)

            # If running in real mode, append output schema instructions so that the LLM knows the required JSON structure
            if settings.LLM_MODE.lower() == "real" and template.output_schema:
                import json
                schema_str = json.dumps(template.output_schema, indent=2)
                rendered_text += (
                    f"\n\nCRITICAL OUTPUT FORMAT REQUIREMENT:\n"
                    f"You MUST return your response as a single, valid JSON object matching the JSON schema below.\n"
                    f"Do not include any explanation, markdown formatting (like ```json), or extra text outside the JSON object.\n"
                    f"Schema:\n{schema_str}"
                )

            self.validator.validate_rendered_prompt(template, rendered_text)
            rendered_hash = self.audit_manager.compute_hash(rendered_text)
            await self.publisher.publish_rendered(prompt_id, rendered_hash, len(rendered_text))
            await self.publisher.publish_validated(prompt_id, "VALIDATED")

            # Determine temperature
            temp = 0.0
            if "scenario_generation" in prompt_id.lower() or "scengen" in prompt_id.lower():
                temp = 0.8
            elif "followup" in prompt_id.lower() or "adaptive" in prompt_id.lower():
                temp = 0.7
            elif "evidence" in prompt_id.lower() or "extraction" in prompt_id.lower():
                temp = 0.1

            # 3. Model Routing & Execution with Retry/Breaker and Validation
            pydantic_success = False
            raw_content = "{}"
            validated_json = {}
            llm_response = {}
            call_count = 0
            provider = None
            selected_model = None
            breaker = None

            from app.core.config import settings
            mode = settings.LLM_MODE.lower()
            max_pydantic_attempts = 2 if mode == "real" else 1
            last_error = None

            for val_attempt in range(max_pydantic_attempts):
                provider, selected_model = self.router.select_provider_and_model(preferred_model)
                await self.publisher.publish_model_selected(prompt_id, provider.provider_name, selected_model)
                
                # Fetch circuit breaker
                breaker_name = provider.provider_name.lower()
                breaker = llm_breaker_pool.get(breaker_name, llm_breaker_pool["openai"])
                if mode != "real":
                    breaker.reset()

                async def call_llm() -> Dict[str, Any]:
                    nonlocal call_count
                    call_count += 1
                    # Pass prompt_id, model, and temperature in options
                    options_dict = {"prompt_id": prompt_id, "model": selected_model, "temperature": temp}
                    options_dict.update(variables)
                    return await provider.generate(
                        rendered_text,
                        options_dict,
                    )

                async def call_with_breaker() -> Dict[str, Any]:
                    return await breaker.execute(call_llm)

                try:
                    await self.publisher.publish_generation_started(prompt_id, selected_model)
                    # Wrap in retry policy
                    llm_response = await execute_with_retry(call_with_breaker, max_retries=3)
                    raw_content = llm_response.get("content", "{}")
                    
                    # Validate output response
                    validated_json = self.response_validator.validate_response(template, raw_content)
                    pydantic_success = True
                    break
                except Exception as e:
                    last_error = e
                    logger.error(
                        f"[APOS FACADE] Attempt {val_attempt + 1} failed for '{prompt_id}' validation/execution: {e}"
                    )
                    logger.error(
                        f"[APOS FACADE] Raw LLM response content was:\n{raw_content}"
                    )
                    if val_attempt == 0 and mode == "real":
                        continue  # Retry validation once
                    else:
                        break

            if not pydantic_success:
                raise PromptOrchestrationFailure(
                    prompt_id,
                    f"LLM execution/validation failed after {max_pydantic_attempts} attempts. Last error: {str(last_error)}"
                )

            latency_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
            await self.publisher.publish_generation_completed(prompt_id, selected_model, latency_ms)
            await self.publisher.publish_validation_succeeded(prompt_id, template.version)

            # Telemetry metrics calculation
            input_tokens = llm_response.get("prompt_tokens", 0)
            output_tokens = llm_response.get("completion_tokens", 0)
            cost = 0.0
            if hasattr(provider, "estimate_cost"):
                cost = provider.estimate_cost(selected_model, input_tokens, output_tokens)
            retry_count = max(0, call_count - 1)
            breaker_state = breaker.state if breaker else "CLOSED"

            logger.info(
                f"[LLM TELEMETRY] Provider: {provider.provider_name}, Model: {selected_model}, "
                f"Latency: {latency_ms}ms, Input Tokens: {input_tokens}, Output Tokens: {output_tokens}, "
                f"Cost: ${cost:.6f}, Success: True, Retry Count: {retry_count}, Breaker State: {breaker_state}"
            )

            # 6. Record Audit Trail
            self.audit_manager.record_audit(
                prompt_id=prompt_id,
                prompt_version=template.version,
                rendered_text=rendered_text,
                provider_name=provider.provider_name,
                model_name=selected_model,
                latency_ms=latency_ms,
                prompt_tokens=input_tokens,
                completion_tokens=output_tokens,
            )

            # Save to Database if session_id is available in variables
            session_id = variables.get("session_id")
            if session_id:
                try:
                    from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
                    from app.infrastructure.persistence.repositories.prompt_repository import PromptRepository as DBPromptRepository
                    async with UnitOfWork() as uow:
                        db_repo = DBPromptRepository(uow.session)
                        await db_repo.save_audit_log(
                            prompt_id=prompt_id,
                            session_id=session_id,
                            template_text=template.template_text,
                            rendered_text=rendered_text,
                            prompt_hash=rendered_hash,
                            model_parameters={
                                "model": selected_model,
                                "temperature": temp,
                                "prompt_version": template.version,
                                "provider": provider.provider_name,
                            },
                            response_payload=validated_json,
                            latency_ms=latency_ms,
                        )
                        await uow.commit()
                    logger.info(f"[APOS DB AUDIT] Successfully persisted audit log for prompt '{prompt_id}'")
                except Exception as db_log_err:
                    logger.warning(f"Could not persist prompt audit log to database: {db_log_err}")

            result = PromptOrchestrationResult(
                prompt_id=prompt_id,
                prompt_version=template.version,
                rendered_prompt=rendered_text,
                rendered_hash=rendered_hash,
                selected_provider=provider.provider_name,
                selected_model=selected_model,
                variables_used=variables,
                validated_response=validated_json,
                latency_ms=latency_ms,
                token_usage={
                    "prompt_tokens": input_tokens,
                    "completion_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens,
                },
            )

            await self.publisher.publish_completed(prompt_id, latency_ms)
            logger.info(f"[APOS FACADE] Successfully orchestrated prompt '{prompt_id}' in {latency_ms}ms")

            return result

        except Exception as e:
            latency_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
            await self.publisher.publish_failed(prompt_id, str(e))
            logger.error(
                f"[LLM TELEMETRY FAILURE] Provider: unknown, Latency: {latency_ms}ms, "
                f"Success: False, Error: {str(e)}"
            )
            logger.error(f"[APOS FACADE] Prompt orchestration failed for '{prompt_id}': {str(e)}")
            raise PromptOrchestrationFailure(prompt_id, str(e))

