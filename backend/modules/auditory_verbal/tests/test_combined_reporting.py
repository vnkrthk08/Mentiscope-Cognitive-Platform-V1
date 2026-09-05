import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_combined_score_calculation_50_50(async_client: AsyncClient):
    """Verify 50/50 combined calculation (Listening + Speaking) via the candidate report API."""
    # 1. Create a live session
    sess_res = await async_client.post(
        "/api/v1/sessions",
        json={"candidate_id": "CAND-REPORT-001", "scenario_id": "SCEN-001"},
    )
    assert sess_res.status_code == 201
    session_id = sess_res.json()["session_id"]

    # 2. Fetch listening questions for the session
    res_q = await async_client.get(f"/api/v1/sessions/{session_id}/listening")
    assert res_q.status_code == 200
    questions = res_q.json()
    assert len(questions) == 4

    # Submit 3 correct answers and 1 incorrect answer -> 75% accuracy
    for idx, q in enumerate(questions):
        q_id = q["question_id"]
        c_idx = q["correct_option_index"]
        sel_idx = c_idx if idx < 3 else (c_idx + 1) % 4
        res = await async_client.post(
            f"/api/v1/sessions/{session_id}/listening/submit",
            json={"question_id": q_id, "selected_option_index": sel_idx, "response_time_ms": 1500},
        )
        assert res.status_code == 200

    # 3. Score speaking module with meaningful transcripts
    score_res = await async_client.post(
        f"/api/v1/sessions/{session_id}/speaking/score",
        json={
            "responses": {
                "SQ1": {
                    "transcript_text": "I choose to re-route battery current to 75% rather than replacing the pack because replacing it exceeds our 45-minute deadline.",
                    "duration_seconds": 15.0,
                    "pause_ratio": 0.20,
                },
                "SQ2": {
                    "transcript_text": "Since the climbing slope is steeper than expected, I adapt by reducing drive motor torque and taking the flatter path.",
                    "duration_seconds": 15.0,
                    "pause_ratio": 0.20,
                },
                "SQ3": {
                    "transcript_text": "In hindsight, we assumed the terrain map was accurate. The key lesson is to always budget a contingency margin.",
                    "duration_seconds": 15.0,
                    "pause_ratio": 0.20,
                },
            }
        },
    )
    assert score_res.status_code == 200

    # 4. Fetch candidate report
    rep_res = await async_client.get(f"/api/v1/reports/{session_id}/candidate")
    assert rep_res.status_code == 200
    report = rep_res.json()

    # Verify report structure & composite calculation
    assert report["audience"] == "Candidate"
    assert report["has_listening"] is True
    assert report["has_speaking"] is True
    assert report["weights"] == {"listening": 0.50, "speaking": 0.50}
    assert report["overall_listening_score"] == 75.0
    assert report["overall_speaking_score"] > 0.0

    expected_combined = round(0.50 * 75.0 + 0.50 * report["overall_speaking_score"], 1)
    assert report["overall_assessment_score"] == expected_combined

    # Verify listening assessment details
    assert "listening_assessment" in report
    l_rep = report["listening_assessment"]
    assert l_rep["overall_listening_score"] == 75.0
    assert l_rep["correct_count"] == 3
    assert l_rep["total_questions"] == 4
    assert len(l_rep["question_breakdown"]) == 4

    # Verify speaking assessment details
    assert "speaking_assessment" in report
    s_rep = report["speaking_assessment"]
    assert s_rep["overall_speaking_score"] == report["overall_speaking_score"]
    assert len(s_rep["question_breakdown"]) == 3


@pytest.mark.asyncio
async def test_combined_score_valid_zero_speaking(async_client: AsyncClient):
    """Verify VALID ZERO handling: candidate scored 0.0 in speaking (empty response) with listening completed."""
    sess_res = await async_client.post(
        "/api/v1/sessions",
        json={"candidate_id": "CAND-ZERO-001", "scenario_id": "SCEN-001"},
    )
    assert sess_res.status_code == 201
    session_id = sess_res.json()["session_id"]

    # Fetch listening questions and answer all correctly -> 100%
    res_q = await async_client.get(f"/api/v1/sessions/{session_id}/listening")
    assert res_q.status_code == 200
    questions = res_q.json()
    assert len(questions) == 4

    for q in questions:
        q_id = q["question_id"]
        c_idx = q["correct_option_index"]
        res = await async_client.post(
            f"/api/v1/sessions/{session_id}/listening/submit",
            json={"question_id": q_id, "selected_option_index": c_idx, "response_time_ms": 1500},
        )
        assert res.status_code == 200

    # Submit empty speaking responses -> 0.0 score
    score_res = await async_client.post(
        f"/api/v1/sessions/{session_id}/speaking/score",
        json={
            "responses": {
                "SQ1": {"transcript_text": "", "duration_seconds": 1.0, "pause_ratio": 1.0},
                "SQ2": {"transcript_text": "", "duration_seconds": 1.0, "pause_ratio": 1.0},
                "SQ3": {"transcript_text": "", "duration_seconds": 1.0, "pause_ratio": 1.0},
            }
        },
    )
    assert score_res.status_code == 200
    assert score_res.json()["overall_speaking_score"] == 0.0

    rep_res = await async_client.get(f"/api/v1/reports/{session_id}/candidate")
    assert rep_res.status_code == 200
    report = rep_res.json()

    assert report["overall_listening_score"] == 100.0
    assert report["overall_speaking_score"] == 0.0
    # 0.50 * 100.0 + 0.50 * 0.0 = 50.0
    assert report["overall_assessment_score"] == 50.0
