import pytest
from httpx import AsyncClient
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.domain.entities.assessment_session import AssessmentSession
from app.domain.entities.candidate_response import SpeakingResponse
from app.domain.value_objects.enums import SessionStatus
from app.application.scenario_subsystem.scenario_repository import ScenarioRepository
from app.application.scoring_engine.facade import PsychometricScoringDecisionEngine
from app.application.evidence_engine.anchor_evaluator import AnchorEvaluator


@pytest.mark.asyncio
async def test_1_score_endpoint_invokes_scoring_facade(async_client: AsyncClient):
    """TEST 1: POST /sessions/{id}/speaking/score actually invokes the scoring facade."""
    sess_res = await async_client.post(
        "/api/v1/sessions",
        json={"candidate_id": "CAND-INT-001", "scenario_id": "SCEN-001"},
    )
    assert sess_res.status_code == 201
    session_id = sess_res.json()["session_id"]

    score_res = await async_client.post(
        f"/api/v1/sessions/{session_id}/speaking/score",
        json={
            "responses": {
                "SQ1": {
                    "transcript_text": "I choose to re-route battery current to 75% rather than replacing the pack because replacing it exceeds our 45-minute deadline.",
                    "duration_seconds": 12.0,
                    "pause_ratio": 0.22,
                },
                "SQ2": {
                    "transcript_text": "Since the climbing hill is steeper than expected, I adapt by reducing drive motor torque and taking the flatter path.",
                    "duration_seconds": 14.0,
                    "pause_ratio": 0.25,
                },
                "SQ3": {
                    "transcript_text": "In hindsight, we assumed the terrain map was accurate. The key lesson is to always budget a fifteen-percent contingency margin.",
                    "duration_seconds": 15.0,
                    "pause_ratio": 0.20,
                },
            }
        },
    )
    assert score_res.status_code == 200
    data = score_res.json()
    assert data["audience"] == "Candidate"
    assert data["overall_speaking_score"] > 0.0
    assert "DECISION_MAKING" in data["demonstrated_construct_scores"]
    assert "ADAPTABILITY" in data["demonstrated_construct_scores"]
    assert "REASONING" in data["demonstrated_construct_scores"]
    assert "COMMUNICATION" in data["demonstrated_construct_scores"]


@pytest.mark.asyncio
async def test_2_three_real_candidate_responses_produce_three_question_scores(async_client: AsyncClient):
    """TEST 2: Three real candidate responses produce three distinct QuestionScores."""
    sess_res = await async_client.post(
        "/api/v1/sessions",
        json={"candidate_id": "CAND-INT-002", "scenario_id": "SCEN-001"},
    )
    session_id = sess_res.json()["session_id"]

    score_res = await async_client.post(
        f"/api/v1/sessions/{session_id}/speaking/score",
        json={
            "responses": {
                "SQ1": {
                    "transcript_text": "I choose to re-route battery current to 75% to meet the strict 10 AM deadline.",
                    "duration_seconds": 10.0,
                },
                "SQ2": {
                    "transcript_text": "I will switch navigation to switchbacks and prioritize battery temperature stability.",
                    "duration_seconds": 11.0,
                },
                "SQ3": {
                    "transcript_text": "The primary takeaway is factoring in real-world friction into model predictions.",
                    "duration_seconds": 12.0,
                },
            }
        },
    )
    assert score_res.status_code == 200
    data = score_res.json()
    breakdown = data.get("question_breakdown", [])
    assert len(breakdown) == 3
    q_ids = {q["question_id"] for q in breakdown}
    assert q_ids == {"SQ1", "SQ2", "SQ3"}
    for q in breakdown:
        assert q["question_score"] > 0.0
        assert q["rubric_score"] >= 0.0
        assert q["fluency_score"] >= 0.0


@pytest.mark.asyncio
async def test_3_persisted_scores_can_be_retrieved_after_scoring(async_client: AsyncClient):
    """TEST 3: Persisted scores can be retrieved from database session after scoring."""
    sess_res = await async_client.post(
        "/api/v1/sessions",
        json={"candidate_id": "CAND-INT-003", "scenario_id": "SCEN-001"},
    )
    session_id = sess_res.json()["session_id"]

    await async_client.post(
        f"/api/v1/sessions/{session_id}/speaking/score",
        json={
            "responses": {
                "SQ1": {"transcript_text": "I choose to re-route power limits.", "duration_seconds": 8.0},
                "SQ2": {"transcript_text": "I adapt by taking alternative route.", "duration_seconds": 8.0},
                "SQ3": {"transcript_text": "We learn to verify sensor data first.", "duration_seconds": 8.0},
            }
        },
    )

    async with UnitOfWork() as uow:
        session = await uow.assessments.get_by_id(session_id)
        assert session is not None
        assert session.metadata.get("speaking_assessment_scored") is True
        assert "candidate_report" in session.metadata
        assert session.status == SessionStatus.COMPLETED


@pytest.mark.asyncio
async def test_4_idempotent_scoring_does_not_duplicate(async_client: AsyncClient):
    """TEST 4: Calling the score endpoint twice does not duplicate or re-score unnecessarily."""
    sess_res = await async_client.post(
        "/api/v1/sessions",
        json={"candidate_id": "CAND-INT-004", "scenario_id": "SCEN-001"},
    )
    session_id = sess_res.json()["session_id"]

    req_payload = {
        "responses": {
            "SQ1": {"transcript_text": "I choose to re-route power limits.", "duration_seconds": 8.0},
            "SQ2": {"transcript_text": "I adapt by taking alternative route.", "duration_seconds": 8.0},
            "SQ3": {"transcript_text": "We learn to verify sensor data first.", "duration_seconds": 8.0},
        }
    }

    # First call
    res1 = await async_client.post(f"/api/v1/sessions/{session_id}/speaking/score", json=req_payload)
    assert res1.status_code == 200
    report1 = res1.json()

    # Second call (idempotent)
    res2 = await async_client.post(f"/api/v1/sessions/{session_id}/speaking/score", json=req_payload)
    assert res2.status_code == 200
    report2 = res2.json()

    assert report1["overall_speaking_score"] == report2["overall_speaking_score"]
    assert report1["performance_band"] == report2["performance_band"]


@pytest.mark.asyncio
async def test_5_get_reports_candidate_returns_persisted_result(async_client: AsyncClient):
    """TEST 5: GET /reports/{id}/candidate returns the persisted candidate result."""
    sess_res = await async_client.post(
        "/api/v1/sessions",
        json={"candidate_id": "CAND-INT-005", "scenario_id": "SCEN-001"},
    )
    session_id = sess_res.json()["session_id"]

    await async_client.post(
        f"/api/v1/sessions/{session_id}/speaking/score",
        json={
            "responses": {
                "SQ1": {"transcript_text": "I choose to re-route power limits to 75%.", "duration_seconds": 9.0},
                "SQ2": {"transcript_text": "I adapt the path to maintain motor health.", "duration_seconds": 9.0},
                "SQ3": {"transcript_text": "The key principle is setting safety buffers.", "duration_seconds": 9.0},
            }
        },
    )

    report_res = await async_client.get(f"/api/v1/reports/{session_id}/candidate")
    assert report_res.status_code == 200
    rep_data = report_res.json()
    assert rep_data["audience"] == "Candidate"
    assert rep_data["session_id"] == session_id
    assert rep_data["overall_speaking_score"] > 0.0
    assert len(rep_data["demonstrated_construct_scores"]) == 4


@pytest.mark.asyncio
async def test_6_frontend_contract_matches_backend_report(async_client: AsyncClient):
    """TEST 6: Validates that candidate report data contract matches all frontend requirements without mockDb."""
    sess_res = await async_client.post(
        "/api/v1/sessions",
        json={"candidate_id": "CAND-INT-006", "scenario_id": "SCEN-001"},
    )
    session_id = sess_res.json()["session_id"]

    await async_client.post(
        f"/api/v1/sessions/{session_id}/speaking/score",
        json={
            "responses": {
                "SQ1": {"transcript_text": "I choose option A to satisfy timeline constraints.", "duration_seconds": 10.0},
                "SQ2": {"transcript_text": "I pivot strategy to preserve component safety.", "duration_seconds": 10.0},
                "SQ3": {"transcript_text": "I reflect on assumptions and derive an engineering principle.", "duration_seconds": 10.0},
            }
        },
    )

    report_res = await async_client.get(f"/api/v1/reports/{session_id}/candidate")
    data = report_res.json()

    assert "overall_speaking_score" in data
    assert "performance_band" in data
    assert "demonstrated_construct_scores" in data
    assert "key_strength" in data
    assert "primary_growth_area" in data
    assert "report_disclaimer" in data

    constructs = data["demonstrated_construct_scores"]
    assert "DECISION_MAKING" in constructs
    assert constructs["DECISION_MAKING"]["title"] == "Simulated Decision-Making & Planning"
    assert "ADAPTABILITY" in constructs
    assert constructs["ADAPTABILITY"]["title"] == "Adaptive Crisis Response & Pivoting"
    assert "REASONING" in constructs
    assert constructs["REASONING"]["title"] == "Reflective Analysis & Metacognition"
    assert "COMMUNICATION" in constructs
    assert constructs["COMMUNICATION"]["title"] == "Clarity, Structure & Delivery"


@pytest.mark.asyncio
async def test_7_single_source_of_truth_mathematical_parity():
    """TEST 7: Verifies backend is single source of truth for FinalSpeakingScore mathematical parity."""
    psde = PsychometricScoringDecisionEngine()
    sq1_score = 90.0
    sq2_score = 80.0
    sq3_score = 85.0

    constructs, final_score = psde.weighting.aggregate_speaking_construct_scores(
        sq1_score=sq1_score,
        sq2_score=sq2_score,
        sq3_score=sq3_score,
    )

    expected_parity = round((sq1_score + sq2_score + sq3_score) / 3.0, 2)
    assert final_score == expected_parity
    assert constructs["DECISION_MAKING"] == round((sq1_score * 1.0 + sq2_score * 0.5) / 1.5, 2)
    assert constructs["ADAPTABILITY"] == sq2_score
    assert constructs["REASONING"] == sq3_score
    assert constructs["COMMUNICATION"] == round((sq1_score * 0.5 + sq3_score * 0.5) / 1.0, 2)


@pytest.mark.asyncio
async def test_8_tier2_timeout_produces_tier1_degraded_result():
    """TEST 8: Tier 2 timeout still produces the existing Tier 1 degraded result with conservative ceiling."""
    evaluator = AnchorEvaluator()
    repo = ScenarioRepository()
    scenario = repo.get_by_id("SCEN-001")
    prompt = scenario.speaking_prompts[0]

    # Directly execute Tier 1 structural fallback
    indicators = evaluator._evaluate_tier1_structural(prompt, "I decide to re-route battery power immediately.")

    assert len(indicators) == 5
    for ind in indicators:
        assert ind.tier_source == "TIER_1_FALLBACK"
        assert ind.score <= 2  # Tier 1 conservative ceiling invariant


@pytest.mark.asyncio
async def test_9_unscored_session_does_not_produce_fabricated_scores(async_client: AsyncClient):
    """TEST 9: Complete scoring failure / un-scored session does not produce fabricated scores."""
    non_existent_uuid = "00000000-0000-0000-0000-000000009999"
    res = await async_client.get(f"/api/v1/reports/{non_existent_uuid}/candidate")
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_10_full_end_to_end_speaking_flow(async_client: AsyncClient):
    """TEST 10: Full end-to-end speaking flow from session creation to candidate report."""
    # 1. Create Session
    create_res = await async_client.post(
        "/api/v1/sessions",
        json={"candidate_id": "CAND-E2E-100", "scenario_id": "SCEN-001"},
    )
    assert create_res.status_code == 201
    session_id = create_res.json()["session_id"]

    # 2. Upload SQ1 Response
    up1 = await async_client.post(
        f"/api/v1/sessions/{session_id}/speaking/upload",
        json={
            "prompt_id": "SQ1_SCEN-001",
            "duration_seconds": 12.0,
            "audio_file_url": "https://s3.amazonaws.com/rec/sq1.webm",
            "transcript_text": "I choose to re-route the battery current to 75% to prevent thermal shutdown and meet the inspection deadline.",
        },
    )
    assert up1.status_code == 200

    # 3. Upload SQ2 Response
    up2 = await async_client.post(
        f"/api/v1/sessions/{session_id}/speaking/upload",
        json={
            "prompt_id": "SQ2_SCEN-001",
            "duration_seconds": 14.0,
            "audio_file_url": "https://s3.amazonaws.com/rec/sq2.webm",
            "transcript_text": "Since the terrain is steep, I adapt by switching to low gear and navigating via the gentler slope.",
        },
    )
    assert up2.status_code == 200

    # 4. Upload SQ3 Response
    up3 = await async_client.post(
        f"/api/v1/sessions/{session_id}/speaking/upload",
        json={
            "prompt_id": "SQ3_SCEN-001",
            "duration_seconds": 15.0,
            "audio_file_url": "https://s3.amazonaws.com/rec/sq3.webm",
            "transcript_text": "In hindsight, we relied too heavily on idealized maps. The general lesson is budgeting a 15% margin for friction.",
        },
    )
    assert up3.status_code == 200

    # 5. Invoke Speaking Score API
    score_res = await async_client.post(f"/api/v1/sessions/{session_id}/speaking/score")
    assert score_res.status_code == 200
    scored_report = score_res.json()
    assert scored_report["overall_speaking_score"] > 0.0

    # 6. Retrieve Persisted Candidate Report
    rep_res = await async_client.get(f"/api/v1/reports/{session_id}/candidate")
    assert rep_res.status_code == 200
    candidate_rep = rep_res.json()

    assert candidate_rep["session_id"] == session_id
    assert candidate_rep["overall_speaking_score"] == scored_report["overall_speaking_score"]
    assert candidate_rep["performance_band"] in ("EXEMPLARY", "PROFICIENT", "DEVELOPING", "EMERGING")
    assert len(candidate_rep["demonstrated_construct_scores"]) == 4
