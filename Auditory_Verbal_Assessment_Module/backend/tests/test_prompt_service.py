import pytest
from app.infrastructure.prompt_service import (
    AIPromptOrchestrationService,
    PromptRepository,
    PromptRenderer,
    PromptValidator,
    ModelRouter,
    MockLLMProvider,
    ResponseValidator,
    PromptAuditManager,
)
from app.domain.exceptions.prompt_exceptions import (
    PromptNotFound,
    MissingVariable,
    ResponseValidationFailure,
    PromptOrchestrationFailure,
)


def test_prompt_repository_and_rendering():
    repo = PromptRepository()
    renderer = PromptRenderer()

    tmpl = repo.get_template("EVIDENCE_EXTRACTION_PROMPT", "1.0.0")
    assert tmpl.prompt_id == "EVIDENCE_EXTRACTION_PROMPT"

    vars_dict = {
        "scenario_title": "Logistics Crisis",
        "transcript_text": "Our team must prioritize safety protocols.",
        "construct_name": "Decision Making",
    }
    rendered = renderer.render(tmpl, vars_dict)
    assert "Logistics Crisis" in rendered
    assert "Decision Making" in rendered


def test_prompt_validator():
    repo = PromptRepository()
    validator = PromptValidator()
    tmpl = repo.get_template("EVIDENCE_EXTRACTION_PROMPT")

    # Missing variable exception
    with pytest.raises(MissingVariable):
        validator.validate_variables(tmpl, {"scenario_title": "Logistics"})


@pytest.mark.asyncio
async def test_mock_llm_provider():
    provider = MockLLMProvider()
    assert provider.health() is True
    assert "gemini-1.5-pro" in provider.supported_models()

    res = await provider.generate("Test prompt", {"prompt_id": "EVIDENCE_EXTRACTION_PROMPT"})
    assert "verbatim_quotes" in res["content"]
    assert res["total_tokens"] > 0


def test_response_validator():
    repo = PromptRepository()
    val = ResponseValidator()
    tmpl = repo.get_template("EVIDENCE_EXTRACTION_PROMPT")

    valid_json = '{"verbatim_quotes": ["quote 1"], "behavioral_indicators": ["ind 1"], "confidence_score": 0.95}'
    parsed = val.validate_response(tmpl, valid_json)
    assert len(parsed["verbatim_quotes"]) == 1

    # Missing required key exception
    invalid_json = '{"verbatim_quotes": ["quote 1"]}'
    with pytest.raises(ResponseValidationFailure):
        val.validate_response(tmpl, invalid_json)


def test_prompt_audit_manager():
    audit = PromptAuditManager()
    h = audit.compute_hash("Rendered text")
    assert len(h) == 16

    rec = audit.record_audit(
        prompt_id="P1",
        prompt_version="1.0.0",
        rendered_text="Rendered text",
        provider_name="GEMINI",
        model_name="gemini-1.5-pro",
        latency_ms=120,
    )
    assert rec.prompt_id == "P1"
    assert rec.rendered_hash == h


@pytest.mark.asyncio
async def test_apos_facade_end_to_end_orchestration():
    apos = AIPromptOrchestrationService()

    vars_dict = {
        "scenario_title": "Logistics Crisis",
        "transcript_text": "Our team must prioritize safety protocols immediately.",
        "construct_name": "DECISION_MAKING",
    }

    res = await apos.execute_prompt(
        prompt_id="EVIDENCE_EXTRACTION_PROMPT",
        variables=vars_dict,
        version="1.0.0",
    )

    assert res.prompt_id == "EVIDENCE_EXTRACTION_PROMPT"
    assert res.selected_provider == "GEMINI"
    assert "verbatim_quotes" in res.validated_response
    assert res.latency_ms >= 0
    assert res.token_usage["total_tokens"] > 0
