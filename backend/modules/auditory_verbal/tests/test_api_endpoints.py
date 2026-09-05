import pytest
from httpx import AsyncClient
from app.core.config import settings
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.infrastructure.persistence.models.orm_models import ScenarioORM


@pytest.fixture(autouse=True)
async def seed_scenario_and_assessment():
    """Auto-seeds a default test scenario to satisfy foreign keys and endpoints execution."""
    async with UnitOfWork() as uow:
        # Seed default Scenario configuration
        existing_scenario = await uow.session.get(ScenarioORM, "SCEN-001")
        if not existing_scenario:
            scenario_orm = ScenarioORM(
                id="SCEN-001",
                title="Emergency Control Room Scenario",
                narrative="Evaluate control room operator response to containment breach.",
                audio_asset={"url": "audio/containment.wav", "duration_seconds": 120.0},
                listening_questions=[
                    {
                        "question_id": "LQ-1",
                        "prompt": "What primary reading triggered the emergency control room audio warning?",
                        "options": ["Acoustic alarm", "Pressure sensor drop", "Visual breach indicator", "Temperature spike"],
                        "correct_option_index": 1,
                        "target_construct": "Working Memory",
                        "secondary_constructs": ["Listening Comprehension"],
                        "question_type": "Recall",
                        "cognitive_objective": "Verbatim recall of pressure sensor drop reading",
                        "difficulty": "INTERMEDIATE",
                        "expected_evidence": {
                            "correct_answer_indicates": "Accurate recall of pressure sensor drop",
                            "distractor_rationale": {"0": "Misheard acoustic alarm", "2": "Confused visual indicator"}
                        },
                        "weight": 1.0,
                        "points": 10,
                        "max_replays": 2,
                    },
                    {
                        "question_id": "LQ-2",
                        "prompt": "Which specific valve component experienced pressure fluctuations during soundcheck?",
                        "options": ["Primary intake valve B", "Secondary exhaust valve C", "Auxiliary cooling valve A", "Main bypass valve D"],
                        "correct_option_index": 0,
                        "target_construct": "Attention",
                        "secondary_constructs": ["Listening Comprehension"],
                        "question_type": "Detail",
                        "cognitive_objective": "Focused attention on specific intake valve detail",
                        "difficulty": "INTERMEDIATE",
                        "expected_evidence": {
                            "correct_answer_indicates": "Focused attention to intake valve B",
                            "distractor_rationale": {"1": "Misheard exhaust valve", "2": "Confused cooling valve"}
                        },
                        "weight": 1.0,
                        "points": 10,
                        "max_replays": 2,
                    },
                    {
                        "question_id": "LQ-3",
                        "prompt": "What central operational dilemma is the control room operator tasked with resolving?",
                        "options": ["Maintaining system containment while managing emergency protocol response time", "Ordering extra office supplies", "Replacing all computer monitors", "Canceling the night shift"],
                        "correct_option_index": 0,
                        "target_construct": "Listening Comprehension",
                        "secondary_constructs": ["Reasoning"],
                        "question_type": "Comprehension",
                        "cognitive_objective": "Comprehension of overall containment trade-off",
                        "difficulty": "INTERMEDIATE",
                        "expected_evidence": {
                            "correct_answer_indicates": "Comprehension of containment dilemma",
                            "distractor_rationale": {"1": "Irrelevant supplies assumption", "2": "Unfounded hardware replacement"}
                        },
                        "weight": 1.0,
                        "points": 10,
                        "max_replays": 2,
                    },
                    {
                        "question_id": "LQ-4",
                        "prompt": "Based on the control room briefing, what consequence follows if the secondary bypass is opened prematurely?",
                        "options": ["Pressure stabilizes temporarily, but secondary filter strain increases", "The entire facility loses electrical power", "External communications are blocked for 24 hours", "Containment seals melt instantly"],
                        "correct_option_index": 0,
                        "target_construct": "Reasoning",
                        "secondary_constructs": ["Listening Comprehension"],
                        "question_type": "Inference",
                        "cognitive_objective": "Inference synthesizing bypass action and filter strain consequence",
                        "difficulty": "INTERMEDIATE",
                        "expected_evidence": {
                            "correct_answer_indicates": "Logical inference of filter strain consequence",
                            "distractor_rationale": {"1": "Exaggerated power loss assumption", "2": "Unfounded comms blockage"}
                        },
                        "weight": 1.0,
                        "points": 10,
                        "max_replays": 2,
                    }
                ],
                speaking_prompts=[
                    {
                        "prompt_id": "SP-1",
                        "title": "Verbal Warning Protocol",
                        "instructions": "State your initial warning protocol broadcast to team.",
                        "time_limit": {"max_seconds": 60.0},
                        "target_constructs": ["COMMUNICATION"],
                        "followup_eligible": True,
                    }
                ],
                follow_up_definitions=[],
                construct_mappings=["DECISION_MAKING", "COMMUNICATION"],
                metadata_json={},
            )
            uow.session.add(scenario_orm)
            await uow.commit()


@pytest.mark.asyncio
async def test_create_and_retrieve_assessment(async_client: AsyncClient):
    # 1. Create Assessment
    payload = {"name": "QA Assessment", "description": "Unit testing REST API"}
    res = await async_client.post("/api/v1/assessments", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert data["name"] == "QA Assessment"
    assessment_id = data["id"]

    # 2. Get Assessment by ID
    res_get = await async_client.get(f"/api/v1/assessments/{assessment_id}")
    assert res_get.status_code == 200
    assert res_get.json()["id"] == assessment_id

    # 3. List Assessments
    res_list = await async_client.get("/api/v1/assessments")
    assert res_list.status_code == 200
    assert len(res_list.json()) >= 1


@pytest.mark.asyncio
async def test_session_lifecycle(async_client: AsyncClient):
    # 1. Create session
    payload = {"candidate_id": "CAND-UNIT", "scenario_id": "SCEN-001"}
    res = await async_client.post("/api/v1/sessions", json=payload)
    assert res.status_code == 201
    session = res.json()
    session_id = session["session_id"]
    assert session["status"] == "INITIALIZED"

    # 2. Get session details
    res_get = await async_client.get(f"/api/v1/sessions/{session_id}")
    assert res_get.status_code == 200
    assert res_get.json()["candidate_id"] == "CAND-UNIT"

    # 3. Start session (transitions CREATED/INITIALIZED to DEVICE_CHECK)
    res_start = await async_client.post(f"/api/v1/sessions/{session_id}/start")
    assert res_start.status_code == 200
    assert res_start.json()["current_stage"] == "DEVICE_CHECK"

    # 4. Pause session
    res_pause = await async_client.post(f"/api/v1/sessions/{session_id}/pause")
    assert res_pause.status_code == 200
    assert res_pause.json()["status"] == "PAUSED"

    # 5. Resume session
    res_resume = await async_client.post(f"/api/v1/sessions/{session_id}/resume")
    assert res_resume.status_code == 200
    assert res_resume.json()["status"] == "IN_PROGRESS"


@pytest.mark.asyncio
async def test_listening_submission(async_client: AsyncClient):
    # Create and start session
    payload = {"candidate_id": "CAND-L", "scenario_id": "SCEN-001"}
    res = await async_client.post("/api/v1/sessions", json=payload)
    session_id = res.json()["session_id"]
    await async_client.post(f"/api/v1/sessions/{session_id}/start")

    # Get listening questions
    res_q = await async_client.get(f"/api/v1/sessions/{session_id}/listening")
    assert res_q.status_code == 200
    assert len(res_q.json()) == 4

    # Submit answer
    submit_payload = {"question_id": "LQ-1", "selected_option_index": 1, "response_time_ms": 1500}
    res_sub = await async_client.post(f"/api/v1/sessions/{session_id}/listening/submit", json=submit_payload)
    assert res_sub.status_code == 200
    assert res_sub.json()["status"] == "SUCCESS"


@pytest.mark.asyncio
async def test_speaking_upload(async_client: AsyncClient):
    payload = {"candidate_id": "CAND-S", "scenario_id": "SCEN-001"}
    res = await async_client.post("/api/v1/sessions", json=payload)
    session_id = res.json()["session_id"]
    await async_client.post(f"/api/v1/sessions/{session_id}/start")

    # Get speaking prompts
    res_p = await async_client.get(f"/api/v1/sessions/{session_id}/speaking")
    assert res_p.status_code == 200
    assert len(res_p.json()) == 3


    # Upload audio response details
    upload_payload = {
        "prompt_id": "SP-1",
        "duration_seconds": 32.4,
        "audio_file_url": "https://url.com/sp.wav",
        "transcript_text": "Warning protocol active.",
    }
    res_up = await async_client.post(f"/api/v1/sessions/{session_id}/speaking/upload", json=upload_payload)
    assert res_up.status_code == 200
    assert res_up.json()["status"] == "SUCCESS"


@pytest.mark.asyncio
async def test_reports_views(async_client: AsyncClient):
    payload = {"candidate_id": "CAND-R", "scenario_id": "SCEN-001"}
    res = await async_client.post("/api/v1/sessions", json=payload)
    session_id = res.json()["session_id"]

    # 1. Main report retrieval
    res_rep = await async_client.get(f"/api/v1/reports/{session_id}")
    assert res_rep.status_code == 200
    assert res_rep.json()["session_id"] == session_id

    # 2. Audience specific presentation views
    for view in ["candidate", "counselor", "research", "administrator"]:
        res_v = await async_client.get(f"/api/v1/reports/{session_id}/{view}")
        assert res_v.status_code == 200


@pytest.mark.asyncio
async def test_research_endpoints(async_client: AsyncClient):
    # 1. Dashboard snapshot
    res_dash = await async_client.get("/api/v1/research/dashboard")
    assert res_dash.status_code == 200
    assert "snapshot_id" in res_dash.json()

    # 2. Validation summary
    res_val = await async_client.get("/api/v1/research/validation")
    assert res_val.status_code == 200

    # 3. Experiments list
    res_exp = await async_client.get("/api/v1/research/experiments")
    assert res_exp.status_code == 200
