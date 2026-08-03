from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from backend.modules.gv.config import MODULE_CONFIG
from backend.modules.gv.item_bank.items import get_item_and_key
from backend.modules.gv.models import GvAnswer, GvEvent, GvResult, GvSession


CONTEXT = {
    "student_id": "DEMO_STUDENT_001",
    "session_id": "DEMO_SESSION_001",
    "module_id": "GV_VISUAL_PROCESSING_BATTERY",
    "module_name": "Visual Processing Battery",
    "construct": "CHC_Gv_Visual_Processing",
    "difficulty": 2,
}


def _contains_forbidden_key(value) -> bool:
    forbidden = {"correct_option_id", "correct_slot", "is_correct", "distractor_type", "answer_key"}
    if isinstance(value, dict):
        if forbidden.intersection(value):
            return True
        return any(_contains_forbidden_key(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_forbidden_key(item) for item in value)
    if isinstance(value, str):
        lowered = value.lower()
        return "_correct" in lowered or "correct_answer" in lowered
    return False


def _event(session_id: str, student_id: str, event_type: str, item_id: str | None = None):
    return {
        "event_id": f"EVT-{uuid4().hex}",
        "student_id": student_id,
        "session_id": session_id,
        "module_id": MODULE_CONFIG.module_id,
        "subtest_id": None,
        "item_id": item_id,
        "event_type": event_type,
        "response": {},
        "correct": None,
        "time_taken": 0,
        "time_since_session_start": 1,
        "attempt_number": 1,
        "difficulty_level": 2,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def _correct_response(session_id: str, difficulty: int, item_id: str):
    record = get_item_and_key(session_id, difficulty, item_id)
    assert record is not None
    if record.answer_key["response_type"] == "single_choice":
        return {"selected_option_id": record.answer_key["correct_option_id"]}
    return {"placements": record.answer_key["solution"]}


def test_start_is_idempotent_and_does_not_expose_answer_keys(client):
    first = client.post("/api/modules/gv/start", json=CONTEXT)
    assert first.status_code == 200, first.text
    payload = first.json()
    assert payload["status"] == "new"
    assert len(payload["practice_items"]) == 4
    assert len(payload["assessment_items"]) == 12
    assert not _contains_forbidden_key(payload)

    second = client.post("/api/modules/gv/start", json=CONTEXT)
    assert second.status_code == 200
    assert second.json()["status"] == "resumed"
    assert second.json()["assessment_items"] == payload["assessment_items"]


def test_scored_answer_acknowledgement_hides_correctness_and_is_idempotent(client):
    start = client.post("/api/modules/gv/start", json=CONTEXT).json()
    item = start["assessment_items"][0]
    request = {
        "submission_id": "SUB-ONE",
        "session_id": CONTEXT["session_id"],
        "item_id": item["item_id"],
        "response": _correct_response(CONTEXT["session_id"], 2, item["item_id"]),
        "practice": False,
        "time_taken_ms": 12000,
        "attempt_number": 1,
        "selection_changes": 0,
        "rotation_attempts": 1,
        "placement_attempts": 0,
        "events": [_event(CONTEXT["session_id"], CONTEXT["student_id"], "item_presented", item["item_id"])],
    }
    response = client.post("/api/modules/gv/answer", json=request)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["accepted"] is True
    assert body["practice_feedback"] is None
    assert "correct" not in body

    duplicate = client.post("/api/modules/gv/answer", json=request)
    assert duplicate.status_code == 200
    assert duplicate.json()["duplicate"] is True


def test_practice_feedback_is_allowed(client):
    start = client.post("/api/modules/gv/start", json=CONTEXT).json()
    item = start["practice_items"][0]
    response = client.post(
        "/api/modules/gv/answer",
        json={
            "submission_id": "SUB-PRACTICE",
            "session_id": CONTEXT["session_id"],
            "item_id": item["item_id"],
            "response": _correct_response(CONTEXT["session_id"], 2, item["item_id"]),
            "practice": True,
            "time_taken_ms": 5000,
            "events": [_event(CONTEXT["session_id"], CONTEXT["student_id"], "practice_started", item["item_id"])],
        },
    )
    assert response.status_code == 200
    assert response.json()["practice_feedback"]["correct"] is True


def test_complete_finish_result_and_persistence(client, db_session):
    start = client.post("/api/modules/gv/start", json=CONTEXT).json()
    for index, item in enumerate(start["assessment_items"]):
        response = _correct_response(CONTEXT["session_id"], 2, item["item_id"])
        piece_count = len(response.get("placements", {}))
        result = client.post(
            "/api/modules/gv/answer",
            json={
                "submission_id": f"SUB-{index}",
                "session_id": CONTEXT["session_id"],
                "item_id": item["item_id"],
                "response": response,
                "practice": False,
                "time_taken_ms": 10000 + index * 250,
                "attempt_number": 1,
                "selection_changes": 0,
                "rotation_attempts": piece_count,
                "placement_attempts": piece_count,
                "events": [
                    _event(CONTEXT["session_id"], CONTEXT["student_id"], "item_presented", item["item_id"]),
                    _event(CONTEXT["session_id"], CONTEXT["student_id"], "item_completed", item["item_id"]),
                ],
            },
        )
        assert result.status_code == 200, result.text

    finish = client.post(
        "/api/modules/gv/finish",
        json={
            "session_id": CONTEXT["session_id"],
            "events": [
                _event(CONTEXT["session_id"], CONTEXT["student_id"], "instructions_viewed"),
                _event(CONTEXT["session_id"], CONTEXT["student_id"], "practice_completed"),
                _event(CONTEXT["session_id"], CONTEXT["student_id"], "subtest_completed"),
            ],
        },
    )
    assert finish.status_code == 200, finish.text
    body = finish.json()
    assert body["status"] == "Completed"
    assert body["metrics"]["raw_score"] == 100.0
    assert body["metrics"]["accuracy"] == 100.0
    assert body["metrics"]["visual_memory_mv"] is None
    assert body["completion_time"] >= 0

    repeated = client.post("/api/modules/gv/finish", json={"session_id": CONTEXT["session_id"]})
    assert repeated.status_code == 200
    assert repeated.json() == body

    fetched = client.get(f"/api/modules/gv/result/{CONTEXT['session_id']}")
    assert fetched.status_code == 200
    assert fetched.json()["metrics"]["raw_score"] == 100.0

    assert db_session.query(GvSession).count() == 1
    assert db_session.query(GvAnswer).filter_by(practice=False).count() == 12
    assert db_session.query(GvResult).count() == 1
    assert db_session.query(GvEvent).count() >= 1 + 12 * 3


def test_finish_rejects_incomplete_session(client):
    client.post("/api/modules/gv/start", json=CONTEXT)
    response = client.post("/api/modules/gv/finish", json={"session_id": CONTEXT["session_id"]})
    assert response.status_code == 409
    assert "incomplete" in response.json()["detail"].lower()


def test_invalid_and_mismatched_sessions(client):
    missing = client.get("/api/modules/gv/result/UNKNOWN")
    assert missing.status_code == 404

    assert client.post("/api/modules/gv/start", json=CONTEXT).status_code == 200
    mismatch = client.post(
        "/api/modules/gv/start",
        json={**CONTEXT, "student_id": "OTHER_STUDENT"},
    )
    assert mismatch.status_code == 409
