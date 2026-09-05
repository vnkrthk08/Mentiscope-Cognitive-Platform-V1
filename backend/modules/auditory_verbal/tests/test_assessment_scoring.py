import pytest
import uuid
from httpx import AsyncClient
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.infrastructure.identity.password_hasher import PasswordHasher
from app.domain.identity.entities.user import User
from app.domain.construct.entities.construct_evaluation import ConstructEvaluation
from app.domain.construct.entities.construct_profile import ConstructProfile
from app.domain.construct.value_objects.construct_confidence import ConstructConfidence as CEEConstructConfidence
from app.domain.construct.value_objects.construct_metadata import ConstructMetadata as CEEConstructMetadata
from app.domain.construct.value_objects.evaluation_reference import EvaluationReference
from app.infrastructure.assessment.normalization.linear_strategy import LinearNormalization
from app.infrastructure.assessment.normalization.percentile_strategy import PercentileNormalization
from app.infrastructure.assessment.normalization.decile_strategy import DecileNormalization
from app.domain.assessment.entities.scoring_policy import ScoringPolicy


@pytest.mark.asyncio
async def test_normalization_strategies():
    linear = LinearNormalization()
    assert linear.normalize(0.85) == 85.0

    percentile = PercentileNormalization()
    assert percentile.normalize(0.75) == 75.0

    decile = DecileNormalization()
    assert decile.normalize(0.65) == 6.5

    with pytest.raises(ValueError):
        linear.normalize(1.5)


@pytest.mark.asyncio
async def test_scoring_policy_entity():
    policy = ScoringPolicy(
        policy_id="test-p",
        framework="CHC",
        policy_name="Test Policy",
        version="1.0.0",
        weight_configuration={"Gf": 1.0},
        normalization_method="LINEAR",
        confidence_method="AVERAGE",
    )
    assert policy.policy_id == "test-p"
    assert policy.framework == "CHC"


@pytest.mark.asyncio
async def test_asr_endpoints_integration(async_client: AsyncClient):
    candidate_username = "candidate_asr_test"

    # 1. Seed candidate user & construct evaluation aggregate
    async with UnitOfWork() as uow:
        hashed = PasswordHasher.hash_password("CandidatePass123")
        cand_role = await uow.roles.get_by_name("Candidate")
        user = User(
            user_id=str(uuid.uuid4()),
            username=candidate_username,
            email="asr_test@mentiscope.com",
            hashed_password=hashed,
            is_active=True,
            is_verified=True,
            roles=[cand_role],
        )
        await uow.users.save(user)

        # Seed ConstructEvaluation
        ref = EvaluationReference(reference_id=str(uuid.uuid4()), reference_type="BEHAVIOR_OBSERVATION")
        conf_vo = CEEConstructConfidence(confidence_score=0.90, support_strength=0.90, evidence_count=1)
        profile = ConstructProfile(
            framework="CHC",
            construct_name="Fluid Intelligence (Gf)",
            supporting_observations=[ref],
            confidence=conf_vo,
            evaluation_summary="summary text",
        )
        meta = CEEConstructMetadata(framework_version="1.0.0", pipeline_version="1.0.0")
        eval_id = str(uuid.uuid4())
        
        evaluation = ConstructEvaluation(
            evaluation_id=eval_id,
            behavior_evidence_id=str(uuid.uuid4()),
            candidate_id=candidate_username,
            assessment_id=str(uuid.uuid4()),
            scenario_id=str(uuid.uuid4()),
            construct_profiles=[profile],
            overall_evaluation_confidence=0.90,
            metadata=meta,
        )
        await uow.construct_evaluations.save(evaluation)
        await uow.commit()

    # 2. Login
    login_res = await async_client.post(
        "/api/v1/auth/login",
        data={"username": candidate_username, "password": "CandidatePass123"},
    )
    assert login_res.status_code == 200
    tokens = login_res.json()
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # 3. POST /assessment/generate
    gen_payload = {
        "construct_evaluation_id": eval_id,
    }
    gen_res = await async_client.post(
        "/api/v1/assessment/generate", json=gen_payload, headers=headers
    )
    assert gen_res.status_code == 200
    gen_data = gen_res.json()
    assert "report_id" in gen_data
    assert "assessment_result_id" in gen_data
    report_id = gen_data["report_id"]
    result_id = gen_data["assessment_result_id"]

    # 4. GET /assessment/reports/{report_id}
    get_rep = await async_client.get(
        f"/api/v1/assessment/reports/{report_id}", headers=headers
    )
    assert get_rep.status_code == 200
    rep_data = get_rep.json()
    assert rep_data["candidate_id"] == candidate_username
    assert len(rep_data["framework_results"]) == 1
    assert rep_data["framework_results"][0]["framework"] == "CHC"

    # 5. GET /assessment/results/{result_id}
    get_res = await async_client.get(
        f"/api/v1/assessment/results/{result_id}", headers=headers
    )
    assert get_res.status_code == 200
    res_data = get_res.json()
    assert res_data["overall_scores"]["CHC"] == 90.0
pre=1.0
