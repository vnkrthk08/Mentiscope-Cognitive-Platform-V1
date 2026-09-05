"""
ACTP Test Suite — Audit, Compliance & Traceability Platform (Phase 14).

Tests for:
  - Domain Value Objects (AuditMetadata, PipelineInvocation, EvidenceReference, ScoreExplanation)
  - Domain Entities (AuditEvent, TraceNode, TraceEdge, DecisionRecord, AuditSession)
  - Application Services (AuditCollectorService, TimelineGenerator, TraceBuilderService)
  - Infrastructure Repositories (AuditSessionRepository, AuditEventRepository, DecisionRecordRepository)
  - Infrastructure Metrics (ACTPMetrics)
  - API router endpoints (/audit/*)
"""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.domain.actp.value_objects.audit_metadata import AuditMetadata
from app.domain.actp.value_objects.pipeline_invocation import PipelineInvocation
from app.domain.actp.value_objects.evidence_reference import EvidenceReference
from app.domain.actp.value_objects.score_explanation import ScoreExplanation
from app.domain.actp.entities.audit_event import AuditEvent
from app.domain.actp.entities.trace_node import TraceNode
from app.domain.actp.entities.trace_edge import TraceEdge
from app.domain.actp.entities.decision_record import DecisionRecord
from app.domain.actp.entities.audit_session import AuditSession


# ---------------------------------------------------------------------------
# 1. Domain Value Object Tests
# ---------------------------------------------------------------------------


class TestACTPValueObjects:
    def test_audit_metadata_defaults(self):
        m = AuditMetadata()
        assert m.environment == "production"
        assert m.ip_address == "127.0.0.1"
        d = m.to_dict()
        assert "schema_version" in d
        assert d["tags"] == {}

    def test_audit_metadata_custom_tags(self):
        m = AuditMetadata(tags={"reconstructed": True, "source": "pipeline"})
        d = m.to_dict()
        assert d["tags"]["reconstructed"] is True

    def test_pipeline_invocation(self):
        inv = PipelineInvocation(
            subsystem="SPEECH",
            provider="deepgram",
            model_name="nova-2",
            version="2.0",
            latency_ms=420.0,
            token_usage={"prompt": 100, "completion": 50},
        )
        d = inv.to_dict()
        assert d["subsystem"] == "SPEECH"
        assert d["provider"] == "deepgram"
        assert d["latency_ms"] == 420.0

    def test_evidence_reference(self):
        er = EvidenceReference(
            evidence_id="ev-001",
            construct_name="fluid_reasoning",
            verbatim_quote="I analyzed the problem.",
            behavioral_indicator="Problem Decomposition",
            confidence=0.92,
        )
        d = er.to_dict()
        assert d["evidence_type"] == "VERBATIM"
        assert d["confidence"] == 0.92

    def test_score_explanation(self):
        se = ScoreExplanation(
            framework_name="CHC",
            construct_name="fluid_reasoning",
            raw_score=75.0,
            normalized_score=75.0,
            weight=0.5,
            scoring_policy_id="policy-v1",
            confidence=0.9,
        )
        d = se.to_dict()
        assert d["weight"] == 0.5
        assert d["scoring_policy_id"] == "policy-v1"


# ---------------------------------------------------------------------------
# 2. Domain Entity Tests
# ---------------------------------------------------------------------------


class TestACTPDomainEntities:
    def test_audit_event_creation(self):
        ev = AuditEvent(
            session_id="ses-001",
            assessment_id="asmnt-001",
            event_type="SPEECH_PROCESSED",
            step_order=3,
            stage_name="Speech Processing",
            payload={"provider": "deepgram"},
        )
        assert ev.event_id  # auto-generated UUID
        assert ev.event_type == "SPEECH_PROCESSED"
        d = ev.to_dict()
        assert d["step_order"] == 3

    def test_trace_node(self):
        node = TraceNode(
            node_id="node-001",
            node_type="SPEECH",
            label="Speech Processed",
            stage="Speech Processing",
        )
        d = node.to_dict()
        assert d["node_type"] == "SPEECH"
        assert d["status"] == "COMPLETED"

    def test_trace_edge(self):
        edge = TraceEdge(
            source_node_id="node-001",
            target_node_id="node-002",
            relation_type="TRANSCRIPTS_AUDIO",
            description="Audio → Transcript",
        )
        d = edge.to_dict()
        assert d["relation_type"] == "TRANSCRIPTS_AUDIO"

    def test_decision_record_hash(self):
        dr = DecisionRecord(
            decision_id="dec-001",
            assessment_id="asmnt-001",
            decision_type="FRAMEWORK_SCORE",
            input_data={"candidate_id": "cand-001"},
            output_decision={"composite_score": 74.5},
        )
        assert dr.reproducible_hash
        assert len(dr.reproducible_hash) == 64  # SHA-256

        # Deterministic: same decision_id, assessment_id, input, output → same hash
        dr2 = DecisionRecord(
            decision_id="dec-001",
            assessment_id="asmnt-001",
            decision_type="FRAMEWORK_SCORE",
            input_data={"candidate_id": "cand-001"},
            output_decision={"composite_score": 74.5},
        )
        assert dr.reproducible_hash == dr2.reproducible_hash

    def test_decision_record_different_data_different_hash(self):
        dr1 = DecisionRecord(
            decision_id="dec-001",
            assessment_id="asmnt-001",
            decision_type="FRAMEWORK_SCORE",
            input_data={"candidate_id": "cand-001"},
            output_decision={"composite_score": 74.5},
        )
        dr2 = DecisionRecord(
            decision_id="dec-002",
            assessment_id="asmnt-001",
            decision_type="FRAMEWORK_SCORE",
            input_data={"candidate_id": "cand-002"},
            output_decision={"composite_score": 80.0},
        )
        assert dr1.reproducible_hash != dr2.reproducible_hash

    def test_audit_session_aggregate(self):
        session = AuditSession(
            assessment_id="asmnt-001",
            candidate_id="cand-001",
            scenario_id="SCN-001",
        )
        assert session.session_status == "ACTIVE"
        assert len(session.events) == 0

        ev = AuditEvent(
            session_id=session.session_id,
            assessment_id="asmnt-001",
            event_type="ASSESSMENT_CREATED",
            step_order=1,
            stage_name="Initialization",
            payload={},
        )
        session.add_event(ev)
        assert len(session.events) == 1

        session.complete()
        assert session.session_status == "COMPLETED"
        assert session.completed_at is not None

    def test_audit_session_validation(self):
        with pytest.raises(ValueError):
            AuditSession(assessment_id="", candidate_id="c", scenario_id="s")

        with pytest.raises(ValueError):
            AuditSession(assessment_id="a", candidate_id="", scenario_id="s")


# ---------------------------------------------------------------------------
# 3. Database Helper
# ---------------------------------------------------------------------------


async def _make_actp_session():
    """Creates a fresh in-memory SQLite database with ACTP tables."""
    import app.infrastructure.actp.orm_models
    import app.infrastructure.persistence.models.orm_models
    from app.infrastructure.persistence.database.base import Base

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    session = factory()
    return engine, session


# ---------------------------------------------------------------------------
# 4. Repository Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_audit_session_repository_save_and_get():
    from app.infrastructure.actp.repositories import AuditSessionRepository, AuditEventRepository

    engine, session = await _make_actp_session()
    try:
        repo = AuditSessionRepository(session)
        event_repo = AuditEventRepository(session)

        audit_session = AuditSession(
            assessment_id="asmnt-repo-001",
            candidate_id="cand-repo-001",
            scenario_id="SCN-001",
            metadata=AuditMetadata(tags={"test": True}),
        )

        ev1 = AuditEvent(
            session_id=audit_session.session_id,
            assessment_id="asmnt-repo-001",
            event_type="ASSESSMENT_CREATED",
            step_order=1,
            stage_name="Initialization",
            payload={"candidate_id": "cand-repo-001"},
        )
        audit_session.add_event(ev1)

        await repo.save(audit_session)
        await event_repo.save(ev1)
        await session.commit()

        fetched = await repo.get_by_id(audit_session.session_id)
        assert fetched is not None
        assert fetched.assessment_id == "asmnt-repo-001"
        assert len(fetched.events) == 1
    finally:
        await session.close()
        await engine.dispose()


@pytest.mark.asyncio
async def test_audit_session_repository_list_and_count():
    from app.infrastructure.actp.repositories import AuditSessionRepository

    engine, session = await _make_actp_session()
    try:
        repo = AuditSessionRepository(session)

        for i in range(3):
            s = AuditSession(
                assessment_id=f"asmnt-list-{i}",
                candidate_id="cand-list",
                scenario_id="SCN-LIST",
            )
            await repo.save(s)
        await session.commit()

        all_sessions = await repo.list_all(limit=50, offset=0)
        assert len(all_sessions) == 3

        count = await repo.count()
        assert count == 3

        filtered = await repo.list_all(candidate_id="cand-list", limit=50, offset=0)
        assert len(filtered) == 3

        count_filtered = await repo.count(candidate_id="nonexistent")
        assert count_filtered == 0
    finally:
        await session.close()
        await engine.dispose()


@pytest.mark.asyncio
async def test_decision_record_repository():
    from app.infrastructure.actp.repositories import DecisionRecordRepository

    engine, session = await _make_actp_session()
    try:
        repo = DecisionRecordRepository(session)

        dr = DecisionRecord(
            decision_id="dec-repo-001",
            assessment_id="asmnt-repo-001",
            decision_type="FRAMEWORK_SCORE",
            input_data={"candidate_id": "cand-repo-001"},
            output_decision={"composite_score": 74.5},
            score_explanations=[
                ScoreExplanation(
                    framework_name="CHC",
                    construct_name="fluid_reasoning",
                    raw_score=75.0,
                    normalized_score=75.0,
                    weight=0.5,
                    scoring_policy_id="policy-v1",
                    confidence=0.9,
                )
            ],
            evidence_references=[
                EvidenceReference(
                    evidence_id="ev-001",
                    construct_name="fluid_reasoning",
                    verbatim_quote="I broke it into three steps.",
                    behavioral_indicator="Problem Decomposition",
                    confidence=0.92,
                )
            ],
            pipeline_invocation=PipelineInvocation(
                subsystem="SCORING",
                provider="MentiscopeEngine",
                model_name="ASRScorer",
                version="3.0",
                latency_ms=120.0,
            ),
        )
        await repo.save(dr)
        await session.commit()

        fetched = await repo.get_by_decision_id("dec-repo-001")
        assert fetched is not None
        assert fetched.decision_type == "FRAMEWORK_SCORE"
        assert fetched.reproducible_hash == dr.reproducible_hash
        assert len(fetched.score_explanations) == 1
        assert len(fetched.evidence_references) == 1
    finally:
        await session.close()
        await engine.dispose()


# ---------------------------------------------------------------------------
# 5. Service Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_audit_collector_service_reconstruct():
    from app.application.actp.services.audit_collector_service import AuditCollectorService

    engine, session = await _make_actp_session()
    try:
        svc = AuditCollectorService(session)

        # Reconstruct from pipeline (will generate synthetic events)
        result = await svc.get_or_reconstruct_session("asmnt-svc-001")
        await session.commit()

        assert result is not None
        assert len(result.events) == 11  # 11 pipeline steps
        assert result.events[0].event_type == "ASSESSMENT_CREATED"
        assert result.events[-1].event_type == "EXPERIMENT_COMPARISON"

        # Second call should fetch from DB, not reconstruct
        result2 = await svc.get_or_reconstruct_session(result.assessment_id)
        assert result2 is not None
        assert len(result2.events) == 11
    finally:
        await session.close()
        await engine.dispose()


@pytest.mark.asyncio
async def test_timeline_generator_service():
    from app.application.actp.services.timeline_generator import TimelineGenerator

    engine, session = await _make_actp_session()
    try:
        tg = TimelineGenerator(session)
        timeline = await tg.generate_timeline("asmnt-timeline-001")
        await session.commit()

        assert timeline["total_steps"] == 11
        assert timeline["assessment_id"] is not None
        assert len(timeline["steps"]) == 11

        # Verify chronological ordering
        for i, step in enumerate(timeline["steps"]):
            assert step["step_order"] == i + 1

        # Verify descriptive titles
        first_step = timeline["steps"][0]
        assert first_step["title"] == "Assessment Created"
        assert first_step["stage_name"] == "Initialization"
    finally:
        await session.close()
        await engine.dispose()


@pytest.mark.asyncio
async def test_trace_builder_service():
    from app.application.actp.services.trace_builder_service import TraceBuilderService

    engine, session = await _make_actp_session()
    try:
        tb = TraceBuilderService(session)
        trace = await tb.generate_trace("asmnt-trace-001")
        await session.commit()

        assert trace["node_count"] == 11
        assert trace["edge_count"] == 10  # N-1 edges for N nodes
        assert len(trace["nodes"]) == 11
        assert len(trace["edges"]) == 10

        # Verify node types
        node_types = {n["node_type"] for n in trace["nodes"]}
        assert "ASSESSMENT" in node_types
        assert "SPEECH" in node_types
        assert "SCORE" in node_types
        assert "REPORT" in node_types

        # Verify edges connect sequentially
        for edge in trace["edges"]:
            assert edge["source_node_id"].startswith("node-")
            assert edge["target_node_id"].startswith("node-")
    finally:
        await session.close()
        await engine.dispose()


@pytest.mark.asyncio
async def test_actp_metrics():
    from app.infrastructure.actp.metrics import ACTPMetrics

    engine, session = await _make_actp_session()
    try:
        metrics = ACTPMetrics(session)

        await metrics.record_audit_session_accessed("ses-001", 11)
        await metrics.record_timeline_generated("asmnt-001", 11)
        await metrics.record_trace_generated("asmnt-001", 11, 10)
        await session.commit()

        # Verify metrics were persisted
        from app.infrastructure.actp.orm_models import ACTPMetricORM
        from sqlalchemy import select

        stmt = select(ACTPMetricORM)
        result = await session.execute(stmt)
        rows = result.scalars().all()
        assert len(rows) == 3

        metric_types = {r.metric_type for r in rows}
        assert "AUDIT_SESSION_ACCESSED" in metric_types
        assert "TIMELINE_GENERATED" in metric_types
        assert "TRACE_GENERATED" in metric_types
    finally:
        await session.close()
        await engine.dispose()


# ---------------------------------------------------------------------------
# 6. API Integration Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_audit_timeline_endpoint(async_client):
    """Tests GET /api/v1/audit/timeline/{assessment_id}."""
    assessment_id = f"asmnt-api-{uuid.uuid4().hex[:8]}"
    res = await async_client.get(f"/api/v1/audit/timeline/{assessment_id}")
    assert res.status_code == 200

    data = res.json()
    assert data["total_steps"] == 11
    assert len(data["steps"]) == 11
    assert data["steps"][0]["event_type"] == "ASSESSMENT_CREATED"
    assert data["steps"][0]["title"] == "Assessment Created"
    assert "generated_at" in data


@pytest.mark.asyncio
async def test_audit_trace_endpoint(async_client):
    """Tests GET /api/v1/audit/trace/{assessment_id}."""
    assessment_id = f"asmnt-trace-api-{uuid.uuid4().hex[:8]}"
    res = await async_client.get(f"/api/v1/audit/trace/{assessment_id}")
    assert res.status_code == 200

    data = res.json()
    assert data["node_count"] == 11
    assert data["edge_count"] == 10
    assert len(data["nodes"]) == 11
    assert len(data["edges"]) == 10

    node_types = {n["node_type"] for n in data["nodes"]}
    assert "ASSESSMENT" in node_types
    assert "SCORE" in node_types
    assert "REPORT" in node_types


@pytest.mark.asyncio
async def test_audit_sessions_list_endpoint(async_client):
    """Tests GET /api/v1/audit/sessions."""
    # First trigger a reconstruction to ensure sessions exist
    assessment_id = f"asmnt-list-api-{uuid.uuid4().hex[:8]}"
    await async_client.get(f"/api/v1/audit/timeline/{assessment_id}")

    res = await async_client.get("/api/v1/audit/sessions?page=1&page_size=50")
    assert res.status_code == 200

    data = res.json()
    assert "sessions" in data
    assert "total" in data
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_audit_decision_endpoint(async_client):
    """Tests GET /api/v1/audit/decision/{decision_id}."""
    # First reconstruct a session to generate the decision record
    assessment_id = f"asmnt-dec-api-{uuid.uuid4().hex[:8]}"
    timeline_res = await async_client.get(f"/api/v1/audit/timeline/{assessment_id}")
    assert timeline_res.status_code == 200
    actual_assessment_id = timeline_res.json()["assessment_id"]

    decision_id = f"dec-{actual_assessment_id[:8]}"
    res = await async_client.get(f"/api/v1/audit/decision/{decision_id}")
    assert res.status_code == 200

    data = res.json()
    assert data["decision_id"] == decision_id
    assert data["decision_type"] == "FRAMEWORK_SCORE"
    assert len(data["score_explanations"]) == 2
    assert len(data["evidence_references"]) == 1
    assert data["reproducible_hash"]
    assert len(data["reproducible_hash"]) == 64


@pytest.mark.asyncio
async def test_audit_decision_not_found(async_client):
    """Tests GET /api/v1/audit/decision/{decision_id} with invalid ID."""
    res = await async_client.get("/api/v1/audit/decision/dec-nonexistent-id-xyz")
    assert res.status_code == 404
