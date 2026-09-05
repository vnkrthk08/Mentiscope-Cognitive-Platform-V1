"""
Integration tests for POST /api/v1/prompt/adaptive-followup-stream SSE endpoint.
"""

import json
import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_adaptive_followup_stream_sse_events():
    """
    Tests that /prompt/adaptive-followup-stream returns text/event-stream
    yielding Event 1 (backchannel) immediately followed by Event 2 (question_ready).
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "scenario_title": "Robotics Competition Battery Thermal Limit Crisis",
            "transcript_text": "I decided to re-route current limits to 75% to prevent the rover battery from overheating.",
            "target_construct": "DECISION_MAKING",
            "session_id": "test_stream_session_001",
        }

        response = await client.post("/api/v1/prompt/adaptive-followup-stream", json=payload)
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("content-type", "")

        events_raw = response.text.strip().split("\n\n")
        assert len(events_raw) >= 2, f"Expected at least 2 SSE events, got: {response.text}"

        # Parse Event 1 (Backchannel)
        event1_lines = events_raw[0].split("\n")
        assert event1_lines[0].startswith("event: backchannel")
        data1 = json.loads(event1_lines[1].replace("data: ", ""))
        assert data1["type"] == "backchannel"
        assert "text" in data1
        assert len(data1["text"]) > 5
        assert data1["category"] in ["COGNITIVE", "ACTION_STANCE", "ANALYTICAL", "FORWARD_LOOKING"]

        # Parse Event 2 (Question Ready)
        event2_lines = events_raw[1].split("\n")
        assert event2_lines[0].startswith("event: question_ready")
        data2 = json.loads(event2_lines[1].replace("data: ", ""))
        assert data2["type"] == "question_ready"
        assert "follow_up_question" in data2
        assert len(data2["follow_up_question"]) > 10
        assert "intent" in data2
        assert "qa_result" in data2


@pytest.mark.asyncio
async def test_unary_endpoint_remains_active():
    """
    Ensures that the existing unary endpoint /prompt/adaptive-followup
    remains completely active and functional alongside the streaming endpoint.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "scenario_title": "Robotics Competition Battery Thermal Limit Crisis",
            "transcript_text": "I decided to re-route current limits to 75% to prevent overheating.",
            "target_construct": "DECISION_MAKING",
            "session_id": "test_unary_session_001",
        }

        response = await client.post("/api/v1/prompt/adaptive-followup", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "follow_up_question" in data
        assert "intent" in data
        assert "qa_result" in data


@pytest.mark.asyncio
async def test_adaptive_followup_stream_error_event_on_downstream_failure():
    """
    Simulates an unexpected downstream failure during follow-up generation and asserts that:
    1. Event 1 (backchannel) is emitted immediately.
    2. Event 2 (error) is emitted with error details rather than hanging.
    """
    from unittest.mock import patch
    from app.application.followup_subsystem.facade import AdaptiveFollowUpSystem

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "scenario_title": "Robotics Competition Battery Thermal Limit Crisis",
            "transcript_text": "I decided to re-route current limits.",
            "target_construct": "DECISION_MAKING",
            "session_id": "test_error_stream_session_002",
        }

        with patch.object(
            AdaptiveFollowUpSystem,
            "generate_followup_question",
            side_effect=RuntimeError("Simulated downstream upstream timeout/failure")
        ):
            response = await client.post("/api/v1/prompt/adaptive-followup-stream", json=payload)
            assert response.status_code == 200
            assert "text/event-stream" in response.headers.get("content-type", "")

            events_raw = response.text.strip().split("\n\n")
            assert len(events_raw) >= 2, f"Expected backchannel + error events, got: {response.text}"

            # Event 1: backchannel must still have arrived immediately
            event1_lines = events_raw[0].split("\n")
            assert event1_lines[0].startswith("event: backchannel")
            data1 = json.loads(event1_lines[1].replace("data: ", ""))
            assert data1["type"] == "backchannel"

            # Event 2: error event emitted without hanging
            event2_lines = events_raw[1].split("\n")
            assert event2_lines[0].startswith("event: error")
            data2 = json.loads(event2_lines[1].replace("data: ", ""))
            assert data2["type"] == "error"
            assert "Simulated downstream upstream timeout/failure" in data2["message"]
