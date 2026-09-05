import pytest
import uuid
from httpx import AsyncClient
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.infrastructure.identity.password_hasher import PasswordHasher
from app.domain.identity.entities.user import User
from app.domain.behavior.entities.behavior_evidence import BehaviorEvidence
from app.domain.behavior.entities.behavior_observation import BehaviorObservation
from app.domain.behavior.entities.evidence_source import EvidenceSource
from app.domain.behavior.value_objects.quote_reference import QuoteReference
from app.domain.behavior.value_objects.evidence_confidence import EvidenceConfidence
from app.domain.behavior.value_objects.evidence_metadata import EvidenceMetadata
from app.infrastructure.construct.mapping_engine import ConstructMappingEngine
from app.infrastructure.construct.confidence_calculator import ConstructConfidenceCalculator
from app.infrastructure.construct.validator import ConstructValidator
from app.domain.construct.entities.construct_profile import ConstructProfile
from app.domain.construct.value_objects.construct_confidence import ConstructConfidence as CEEConstructConfidence
from app.domain.construct.value_objects.evaluation_reference import EvaluationReference


@pytest.mark.asyncio
async def test_construct_mapping_rules():
    # Verify leadership maps to Personality: Leadership and RIASEC: Enterprising
    mappings = ConstructMappingEngine.get_mappings("leadership")
    assert len(mappings) == 2
    assert mappings[0][0] == "PERSONALITY"
    assert mappings[0][1] == "Leadership"
    assert mappings[1][0] == "RIASEC"
    assert mappings[1][1] == "Enterprising"


@pytest.mark.asyncio
async def test_construct_confidence_calculator():
    # Setup mock observation
    quote = QuoteReference(quote="Hello", start_word_index=0, end_word_index=1, start_time=0.0, end_time=1.0)
    conf = EvidenceConfidence(overall=0.9, supporting_score=0.9, consistency_score=1.0)
    obs = BehaviorObservation(
        observation_id="obs-1",
        behavior_type="Leadership",
        description="description",
        supporting_quotes=[quote],
        confidence=conf,
    )

    # 1 observation (support strength starting baseline 0.75 for 1 observation)
    conf_vo = ConstructConfidenceCalculator.calculate([obs], "Personality")
    assert conf_vo.evidence_count == 1
    assert conf_vo.support_strength == 0.75
    assert conf_vo.confidence_score == 0.675


@pytest.mark.asyncio
async def test_construct_validator_rejection():
    ref = EvaluationReference(reference_id="ref-1", reference_type="OBSERVATION")
    conf = CEEConstructConfidence(confidence_score=0.8, support_strength=0.8, evidence_count=1)
    
    # 1. Invalid framework
    p_invalid = ConstructProfile(
        framework="INVALID_FRAMEWORK",
        construct_name="Test",
        supporting_observations=[ref],
        confidence=conf,
        evaluation_summary="summary",
    )
    valid, errors = ConstructValidator.validate_profiles([p_invalid])
    assert len(valid) == 0
    assert "invalid" in errors[0].lower()


@pytest.mark.asyncio
async def test_cee_endpoints_integration(async_client: AsyncClient):
    candidate_username = "candidate_cee_test"

    # 1. Seed candidate user & behavior evidence record
    async with UnitOfWork() as uow:
        hashed = PasswordHasher.hash_password("CandidatePass123")
        cand_role = await uow.roles.get_by_name("Candidate")
        user = User(
            user_id=str(uuid.uuid4()),
            username=candidate_username,
            email="cee_test@mentiscope.com",
            hashed_password=hashed,
            is_active=True,
            is_verified=True,
            roles=[cand_role],
        )
        await uow.users.save(user)

        # Seed BehaviorEvidence
        quote = QuoteReference(
            quote="Hello, welcome to MentiScope assessment engine.",
            start_word_index=0,
            end_word_index=5,
            start_time=0.0,
            end_time=5.2,
        )
        conf = EvidenceConfidence(overall=0.95, supporting_score=0.95, consistency_score=1.0)
        obs = BehaviorObservation(
            observation_id=str(uuid.uuid4()),
            behavior_type="Leadership",
            description="Candidate demonstrates leadership by greeting.",
            supporting_quotes=[quote],
            confidence=conf,
            linked_constructs=["Leadership"],
        )
        src = EvidenceSource(source_type="PROMPT_RESPONSE", source_id=str(uuid.uuid4()), provider="openai")
        meta = EvidenceMetadata(pipeline_version="1.0.0", model_version="gpt-5-turbo")
        evidence_id = str(uuid.uuid4())
        
        evidence = BehaviorEvidence(
            evidence_id=evidence_id,
            transcript_id=str(uuid.uuid4()),
            prompt_execution_id=str(uuid.uuid4()),
            candidate_id=candidate_username,
            assessment_id=str(uuid.uuid4()),
            scenario_id=str(uuid.uuid4()),
            construct_candidates=["Leadership"],
            behavior_observations=[obs],
            evidence_sources=[src],
            overall_confidence=0.95,
            metadata=meta,
        )
        await uow.behavior_evidences.save(evidence)
        await uow.commit()

    # 2. Login
    login_res = await async_client.post(
        "/api/v1/auth/login",
        data={"username": candidate_username, "password": "CandidatePass123"},
    )
    assert login_res.status_code == 200
    tokens = login_res.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # 3. POST /construct/evaluate
    eval_payload = {
        "behavior_evidence_id": evidence_id,
    }
    eval_res = await async_client.post(
        "/api/v1/construct/evaluate", json=eval_payload, headers=headers
    )
    assert eval_res.status_code == 200
    eval_data = eval_res.json()
    assert "evaluation_id" in eval_data
    assert eval_data["profiles_count"] == 2  # mapped to PERSONALITY and RIASEC
    evaluation_id = eval_data["evaluation_id"]

    # 4. GET /construct/evaluations/{evaluation_id}
    get_res = await async_client.get(
        f"/api/v1/construct/evaluations/{evaluation_id}", headers=headers
    )
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert get_data["candidate_id"] == candidate_username
    assert len(get_data["construct_profiles"]) == 2
pre=1.0
