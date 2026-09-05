import pytest
from httpx import AsyncClient
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.domain.value_objects.enums import SessionStatus


@pytest.mark.asyncio
async def test_combined_reporting_valid_zero_and_50_50_cases(async_client: AsyncClient):
    """Validates that candidate reports ALWAYS use 50/50 dual-domain weighting with unattempted modules = 0.0."""

    # -------------------------------------------------------------
    # TEST 1: Listening = 100, Speaking = missing
    # Expected: Listening = 100.0, Speaking = 0.0, Overall = 50.0, Weights = 50/50
    # -------------------------------------------------------------
    sess_res1 = await async_client.post(
        "/api/v1/sessions", json={"candidate_id": "CAND-CASE-1", "scenario_id": "SCEN-001"}
    )
    assert sess_res1.status_code == 201
    sid1 = sess_res1.json()["session_id"]

    async with UnitOfWork() as uow:
        s1 = await uow.assessments.get_by_id(sid1)
        s1.metadata["overall_listening_score"] = 100.0
        s1.metadata["listening_results"] = {"raw_accuracy_percentage": 100.0, "responses": {}}
        # No speaking module scored
        await uow.assessments.save(s1)
        await uow.commit()

    res1 = await async_client.get(f"/api/v1/reports/{sid1}/candidate")
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["has_listening"] is True
    assert data1["has_speaking"] is False
    assert data1["overall_listening_score"] == 100.0
    assert data1["overall_speaking_score"] == 0.0
    assert data1["overall_assessment_score"] == 50.0
    assert data1["weights"] == {"listening": 0.50, "speaking": 0.50}

    # -------------------------------------------------------------
    # TEST 2: Listening = missing, Speaking = 11.2
    # Expected: Listening = 0.0, Speaking = 11.2, Overall = 5.6, Weights = 50/50
    # -------------------------------------------------------------
    sess_res2 = await async_client.post(
        "/api/v1/sessions", json={"candidate_id": "CAND-CASE-2", "scenario_id": "SCEN-001"}
    )
    assert sess_res2.status_code == 201
    sid2 = sess_res2.json()["session_id"]

    async with UnitOfWork() as uow:
        s2 = await uow.assessments.get_by_id(sid2)
        # No listening module scored
        s2.metadata["speaking_assessment_scored"] = True
        s2.metadata["overall_speaking_score"] = 11.2
        s2.metadata["candidate_report"] = {
            "overall_speaking_score": 11.2,
            "demonstrated_construct_scores": {
                "DECISION_MAKING": {"score": 11.2},
                "ADAPTABILITY": {"score": 11.2},
                "REASONING": {"score": 11.2},
                "COMMUNICATION": {"score": 11.2},
            },
            "question_breakdown": [],
        }
        await uow.assessments.save(s2)
        await uow.commit()

    res2 = await async_client.get(f"/api/v1/reports/{sid2}/candidate")
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["has_listening"] is False
    assert data2["has_speaking"] is True
    assert data2["overall_listening_score"] == 0.0
    assert data2["overall_speaking_score"] == 11.2
    assert data2["overall_assessment_score"] == 5.6
    assert data2["weights"] == {"listening": 0.50, "speaking": 0.50}

    # -------------------------------------------------------------
    # TEST 3: Listening = 100, Speaking = 0 (both completed)
    # Expected: Listening = 100.0, Speaking = 0.0, Overall = 50.0, Weights = 50/50
    # -------------------------------------------------------------
    sess_res3 = await async_client.post(
        "/api/v1/sessions", json={"candidate_id": "CAND-CASE-3", "scenario_id": "SCEN-001"}
    )
    assert sess_res3.status_code == 201
    sid3 = sess_res3.json()["session_id"]

    async with UnitOfWork() as uow:
        s3 = await uow.assessments.get_by_id(sid3)
        s3.metadata["overall_listening_score"] = 100.0
        s3.metadata["listening_results"] = {"raw_accuracy_percentage": 100.0, "responses": {}}
        s3.metadata["speaking_assessment_scored"] = True
        s3.metadata["overall_speaking_score"] = 0.0
        s3.metadata["candidate_report"] = {
            "overall_speaking_score": 0.0,
            "demonstrated_construct_scores": {
                "DECISION_MAKING": {"score": 0.0},
                "ADAPTABILITY": {"score": 0.0},
                "REASONING": {"score": 0.0},
                "COMMUNICATION": {"score": 0.0},
            },
            "question_breakdown": [],
        }
        await uow.assessments.save(s3)
        await uow.commit()

    res3 = await async_client.get(f"/api/v1/reports/{sid3}/candidate")
    assert res3.status_code == 200
    data3 = res3.json()
    assert data3["has_listening"] is True
    assert data3["has_speaking"] is True
    assert data3["overall_listening_score"] == 100.0
    assert data3["overall_speaking_score"] == 0.0
    assert data3["overall_assessment_score"] == 50.0
    assert data3["weights"] == {"listening": 0.50, "speaking": 0.50}

    # -------------------------------------------------------------
    # TEST 4: Listening = 0, Speaking = 100 (both completed)
    # Expected: Listening = 0.0, Speaking = 100.0, Overall = 50.0, Weights = 50/50
    # -------------------------------------------------------------
    sess_res4 = await async_client.post(
        "/api/v1/sessions", json={"candidate_id": "CAND-CASE-4", "scenario_id": "SCEN-001"}
    )
    assert sess_res4.status_code == 201
    sid4 = sess_res4.json()["session_id"]

    async with UnitOfWork() as uow:
        s4 = await uow.assessments.get_by_id(sid4)
        s4.metadata["overall_listening_score"] = 0.0
        s4.metadata["listening_results"] = {"raw_accuracy_percentage": 0.0, "responses": {}}
        s4.metadata["speaking_assessment_scored"] = True
        s4.metadata["overall_speaking_score"] = 100.0
        s4.metadata["candidate_report"] = {
            "overall_speaking_score": 100.0,
            "demonstrated_construct_scores": {
                "DECISION_MAKING": {"score": 100.0},
                "ADAPTABILITY": {"score": 100.0},
                "REASONING": {"score": 100.0},
                "COMMUNICATION": {"score": 100.0},
            },
            "question_breakdown": [],
        }
        await uow.assessments.save(s4)
        await uow.commit()

    res4 = await async_client.get(f"/api/v1/reports/{sid4}/candidate")
    assert res4.status_code == 200
    data4 = res4.json()
    assert data4["has_listening"] is True
    assert data4["has_speaking"] is True
    assert data4["overall_listening_score"] == 0.0
    assert data4["overall_speaking_score"] == 100.0
    assert data4["overall_assessment_score"] == 50.0
    assert data4["weights"] == {"listening": 0.50, "speaking": 0.50}

    # -------------------------------------------------------------
    # TEST 5: Listening = 0, Speaking = 0 (both completed)
    # Expected: Listening = 0.0, Speaking = 0.0, Overall = 0.0, Weights = 50/50
    # -------------------------------------------------------------
    sess_res5 = await async_client.post(
        "/api/v1/sessions", json={"candidate_id": "CAND-CASE-5", "scenario_id": "SCEN-001"}
    )
    assert sess_res5.status_code == 201
    sid5 = sess_res5.json()["session_id"]

    async with UnitOfWork() as uow:
        s5 = await uow.assessments.get_by_id(sid5)
        s5.metadata["overall_listening_score"] = 0.0
        s5.metadata["listening_results"] = {"raw_accuracy_percentage": 0.0, "responses": {}}
        s5.metadata["speaking_assessment_scored"] = True
        s5.metadata["overall_speaking_score"] = 0.0
        s5.metadata["candidate_report"] = {
            "overall_speaking_score": 0.0,
            "demonstrated_construct_scores": {
                "DECISION_MAKING": {"score": 0.0},
                "ADAPTABILITY": {"score": 0.0},
                "REASONING": {"score": 0.0},
                "COMMUNICATION": {"score": 0.0},
            },
            "question_breakdown": [],
        }
        await uow.assessments.save(s5)
        await uow.commit()

    res5 = await async_client.get(f"/api/v1/reports/{sid5}/candidate")
    assert res5.status_code == 200
    data5 = res5.json()
    assert data5["has_listening"] is True
    assert data5["has_speaking"] is True
    assert data5["overall_listening_score"] == 0.0
    assert data5["overall_speaking_score"] == 0.0
    assert data5["overall_assessment_score"] == 0.0
    assert data5["weights"] == {"listening": 0.50, "speaking": 0.50}

    # -------------------------------------------------------------
    # TEST 6: Listening = 75, Speaking = 48.8
    # Expected: Listening = 75.0, Speaking = 48.8, Overall = 61.9, Weights = 50/50
    # -------------------------------------------------------------
    sess_res6 = await async_client.post(
        "/api/v1/sessions", json={"candidate_id": "CAND-CASE-6", "scenario_id": "SCEN-001"}
    )
    assert sess_res6.status_code == 201
    sid6 = sess_res6.json()["session_id"]

    async with UnitOfWork() as uow:
        s6 = await uow.assessments.get_by_id(sid6)
        s6.metadata["overall_listening_score"] = 75.0
        s6.metadata["listening_results"] = {"raw_accuracy_percentage": 75.0, "responses": {}}
        s6.metadata["speaking_assessment_scored"] = True
        s6.metadata["overall_speaking_score"] = 48.8
        s6.metadata["candidate_report"] = {
            "overall_speaking_score": 48.8,
            "demonstrated_construct_scores": {
                "DECISION_MAKING": {"score": 48.8},
                "ADAPTABILITY": {"score": 48.8},
                "REASONING": {"score": 48.8},
                "COMMUNICATION": {"score": 48.8},
            },
            "question_breakdown": [],
        }
        await uow.assessments.save(s6)
        await uow.commit()

    res6 = await async_client.get(f"/api/v1/reports/{sid6}/candidate")
    assert res6.status_code == 200
    data6 = res6.json()
    assert data6["has_listening"] is True
    assert data6["has_speaking"] is True
    assert data6["overall_listening_score"] == 75.0
    assert data6["overall_speaking_score"] == 48.8
    assert data6["overall_assessment_score"] == 61.9
    assert data6["weights"] == {"listening": 0.50, "speaking": 0.50}

    # -------------------------------------------------------------
    # TEST 7: Both modules missing
    # Expected: Listening = 0.0, Speaking = 0.0, Overall = 0.0, Weights = 50/50
    # -------------------------------------------------------------
    sess_res7 = await async_client.post(
        "/api/v1/sessions", json={"candidate_id": "CAND-CASE-7", "scenario_id": "SCEN-001"}
    )
    assert sess_res7.status_code == 201
    sid7 = sess_res7.json()["session_id"]

    res7 = await async_client.get(f"/api/v1/reports/{sid7}/candidate")
    assert res7.status_code == 200
    data7 = res7.json()
    assert data7["has_listening"] is False
    assert data7["has_speaking"] is False
    assert data7["overall_listening_score"] == 0.0
    assert data7["overall_speaking_score"] == 0.0
    assert data7["overall_assessment_score"] == 0.0
    assert data7["weights"] == {"listening": 0.50, "speaking": 0.50}
