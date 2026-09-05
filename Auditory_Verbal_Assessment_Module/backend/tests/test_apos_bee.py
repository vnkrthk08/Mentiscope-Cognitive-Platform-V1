import pytest
import uuid
import json
from httpx import AsyncClient
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.infrastructure.identity.password_hasher import PasswordHasher
from app.domain.identity.entities.user import User
from app.domain.speech.entities.transcript import Transcript
from app.domain.speech.value_objects.provider_result import ProviderResult as SpeechProviderResult
from app.domain.speech.value_objects.language import Language as SpeechLanguage
from app.domain.speech.value_objects.confidence_score import ConfidenceScore as SpeechConfidenceScore
from app.domain.speech.value_objects.transcript_metadata import TranscriptMetadata as SpeechTranscriptMetadata
from app.infrastructure.prompt.template_engine import template_engine
from app.infrastructure.prompt.strategies.provider_selection import LLMSelectionStrategy
from app.infrastructure.prompt.response_normalizer import LLMResponseNormalizer
from app.infrastructure.behavior.extractors.behavior_extractor import BehaviorExtractor
from app.infrastructure.behavior.validator import EvidenceValidator
from app.domain.behavior.entities.behavior_observation import BehaviorObservation
from app.domain.behavior.value_objects.quote_reference import QuoteReference
from app.domain.behavior.value_objects.evidence_confidence import EvidenceConfidence


@pytest.mark.asyncio
async def test_prompt_template_engine():
    # Substitute check
    vars_map = {
        "candidate_id": "cand-99",
        "assessment_id": "assess-88",
        "scenario_text": "Scenario context details.",
        "transcript_text": "Sample text audio transcript.",
    }
    rendered = template_engine.render("default-assessment-template", vars_map)
    assert "cand-99" in rendered
    assert "assess-88" in rendered
    assert "Sample text audio" in rendered

    with pytest.raises(ValueError):
        # Missing variable error
        template_engine.render("default-assessment-template", {"candidate_id": "test"})


@pytest.mark.asyncio
async def test_llm_selection_strategy():
    name_default, _ = LLMSelectionStrategy.resolve_provider("DEFAULT")
    assert name_default == "openrouter"

    name_cheapest, _ = LLMSelectionStrategy.resolve_provider("LOWEST_COST", input_tokens=1000)
    assert name_cheapest == "gemini"


@pytest.mark.asyncio
async def test_llm_response_normalizers():
    raw_openai = {
        "choices": [
            {
                "message": {
                    "content": "OpenAI mock reply content",
                    "role": "assistant",
                }
            }
        ],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
        }
    }
    txt, inp, out = LLMResponseNormalizer.normalize("openai", raw_openai)
    assert txt == "OpenAI mock reply content"
    assert inp == 100
    assert out == 50


@pytest.mark.asyncio
async def test_behavior_extractor_and_validator():
    mock_llm_json = {
        "behaviors": [
            {
                "category": "Communication",
                "description": "Candidate introduces task clearly.",
                "quote": "Hello welcome.",
                "start_word_index": 0,
                "end_word_index": 2,
                "start_time": 0.0,
                "end_time": 1.5,
                "confidence": 0.95,
                "linked_constructs": ["Communication"],
            },
            {
                "category": "Leadership",
                "description": "Low confidence duplicate check element.",
                "quote": "",  # Missing quote
                "start_word_index": 0,
                "end_word_index": 0,
                "start_time": 0.0,
                "end_time": 0.0,
                "confidence": 0.20,  # Low confidence (<0.3)
                "linked_constructs": ["Leadership"],
            }
        ]
    }
    raw_obs = BehaviorExtractor.extract_observations(json.dumps(mock_llm_json))
    assert len(raw_obs) == 2

    # Run validation filtering
    valid, quarantined = EvidenceValidator.validate_observations(raw_obs)
    assert len(valid) == 1
    assert valid[0].behavior_type == "Communication"
    assert len(quarantined) == 1  # Leadership failed due to low confidence


@pytest.mark.asyncio
async def test_apos_bee_endpoints_integration(async_client: AsyncClient):
    candidate_username = "candidate_apos_bee_test"
    
    # 1. Seed candidate user & speech transcript
    async with UnitOfWork() as uow:
        hashed = PasswordHasher.hash_password("CandidatePass123")
        cand_role = await uow.roles.get_by_name("Candidate")
        user = User(
            user_id=str(uuid.uuid4()),
            username=candidate_username,
            email="apos_bee@mentiscope.com",
            hashed_password=hashed,
            is_active=True,
            is_verified=True,
            roles=[cand_role],
        )
        await uow.users.save(user)

        # Seed speech transcript
        sp_res = SpeechProviderResult(
            provider_name="whisper",
            provider_version="1.0.0",
            model_name="default",
            request_id="req-1",
            processing_time=1.2,
            api_latency=100.0,
            estimated_cost=0.01,
            billing_units=1,
        )
        lang = SpeechLanguage(language_code="en", confidence=1.0)
        conf = SpeechConfidenceScore(overall_score=0.98, per_word_scores=[0.98])
        meta = SpeechTranscriptMetadata(
            normalization_version="1.0.0",
            provider_version="1.0.0",
            processing_pipeline_version="1.0.0",
        )
        transcript_id = str(uuid.uuid4())
        transcript = Transcript(
            transcript_id=transcript_id,
            asset_id=str(uuid.uuid4()),
            session_id=str(uuid.uuid4()),
            assessment_id=str(uuid.uuid4()),
            candidate_id=candidate_username,
            provider_result=sp_res,
            language=lang,
            confidence_score=conf,
            transcript_metadata=meta,
            transcript_text="Hello, welcome to MentiScope assessment engine.",
        )
        await uow.speech_transcripts.save(transcript)
        await uow.commit()

    # 2. Login
    login_res = await async_client.post(
        "/api/v1/auth/login",
        data={"username": candidate_username, "password": "CandidatePass123"},
    )
    assert login_res.status_code == 200
    tokens = login_res.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # 3. POST /prompt/execute (Starts prompt execution pipeline)
    exec_payload = {
        "asset_id": transcript_id,
        "selection_policy": "DEFAULT",
    }
    exec_res = await async_client.post(
        "/api/v1/prompt/execute", json=exec_payload, headers=headers
    )
    assert exec_res.status_code == 202
    execution_id = exec_res.json()["job_id"]
    assert execution_id is not None

    # 4. POST /behavior/extract (Starts behavior extraction pipeline)
    ext_payload = {
        "prompt_execution_id": execution_id,
    }
    ext_res = await async_client.post(
        "/api/v1/behavior/extract", json=ext_payload, headers=headers
    )
    assert ext_res.status_code == 200
    ext_data = ext_res.json()
    assert "evidence_id" in ext_data
    assert ext_data["validation_passed"] is True
    assert ext_data["observations_count"] == 1
    evidence_id = ext_data["evidence_id"]

    # 5. GET /behavior/evidence/{evidence_id} (Retrieve aggregate)
    get_res = await async_client.get(
        f"/api/v1/behavior/evidence/{evidence_id}", headers=headers
    )
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert get_data["candidate_id"] == candidate_username
    assert len(get_data["behavior_observations"]) == 1
    assert get_data["behavior_observations"][0]["behavior_type"] == "Leadership"
