"""
RAIP Test Suite — Research Analytics & Insights Platform (Phase 12).

Tests for:
  - Domain models & Value objects
  - AnalyticsAggregatorService (read-only aggregation)
  - AnalyticsRepository (save/fetch snapshots)
  - API router endpoints (/analytics/dashboard, /analytics/assessments, etc.)
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.domain.analytics.value_objects.time_window import TimeWindow
from app.domain.analytics.models.assessment_analytics import AssessmentAnalytics, TrendPoint
from app.domain.analytics.models.framework_analytics import FrameworkAnalytics, FrameworkMetrics
from app.domain.analytics.models.evidence_analytics import EvidenceAnalytics, ObservationFrequency
from app.domain.analytics.models.research_analytics import ResearchAnalytics, ReviewerWorkload
from app.domain.analytics.models.platform_analytics import PlatformAnalytics
from app.domain.analytics.models.dashboard_snapshot import DashboardSnapshot


# ---------------------------------------------------------------------------
# Domain Model Tests
# ---------------------------------------------------------------------------


class TestRAIPDomainModels:
    def test_time_window_values(self):
        assert TimeWindow.DAILY == "daily"
        assert TimeWindow.WEEKLY == "weekly"
        assert TimeWindow.MONTHLY == "monthly"
        assert TimeWindow.ALL_TIME == "all_time"

    def test_assessment_analytics_default(self):
        aa = AssessmentAnalytics()
        assert aa.total_assessments == 0
        assert aa.overall_completion_rate == 0.0
        assert aa.by_scenario == {}
        assert aa.trend_series == []

    def test_framework_analytics_initialization(self):
        fa = FrameworkAnalytics()
        assert fa.chc.framework_name == "CHC"
        assert fa.riasec.framework_name == "RIASEC"
        assert fa.personality.framework_name == "Personality"
        assert fa.emotional_regulation.framework_name == "Emotional Regulation"

    def test_evidence_analytics_default(self):
        ea = EvidenceAnalytics()
        assert ea.total_evidence_count == 0
        assert ea.average_quality_score == 0.0
        assert ea.top_observation_frequencies == []

    def test_research_analytics_default(self):
        ra = ResearchAnalytics()
        assert ra.total_validation_datasets == 0
        assert ra.reviewer_workloads == []

    def test_platform_analytics_default(self):
        pa = PlatformAnalytics()
        assert pa.avg_speech_latency_ms == 0.0
        assert pa.pipeline_completion_rate == 0.0

    def test_dashboard_snapshot_creation(self):
        snap = DashboardSnapshot(snapshot_id="snap-123", time_window="all_time")
        assert snap.snapshot_id == "snap-123"
        assert snap.time_window == "all_time"
        assert snap.assessments.total_assessments == 0


# ---------------------------------------------------------------------------
# Database Helper
# ---------------------------------------------------------------------------


async def _make_session():
    """Helper to create a fresh in-memory SQLite database with registered tables."""
    import app.infrastructure.persistence.models.orm_models
    import app.infrastructure.assessment.orm_models
    import app.infrastructure.research.orm_models
    import app.infrastructure.behavior.orm_models
    import app.infrastructure.analytics.orm_models

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
# Aggregator & Repository Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_analytics_aggregator_empty_database():
    from app.application.analytics.services.analytics_aggregator import AnalyticsAggregatorService

    engine, session = await _make_session()
    try:
        svc = AnalyticsAggregatorService(session)
        snap = await svc.aggregate_dashboard(TimeWindow.ALL_TIME)
        assert snap.snapshot_id.startswith("snap-")
        assert snap.assessments.total_assessments == 0
        assert snap.frameworks.chc.framework_name == "CHC"
        assert snap.evidence.total_evidence_count == 0
        assert snap.research.total_validation_datasets == 0
        assert snap.platform.pipeline_completion_rate > 0  # default baseline
    finally:
        await session.close()
        await engine.dispose()


@pytest.mark.asyncio
async def test_analytics_repository_save_and_get():
    from app.application.analytics.services.analytics_aggregator import AnalyticsAggregatorService
    from app.infrastructure.analytics.repository import AnalyticsRepository

    engine, session = await _make_session()
    try:
        svc = AnalyticsAggregatorService(session)
        snap = await svc.aggregate_dashboard(TimeWindow.ALL_TIME)

        repo = AnalyticsRepository(session)
        await repo.save_snapshot(snap)
        await session.commit()

        latest = await repo.get_latest_snapshot("all_time")
        assert latest is not None
        assert latest.snapshot_id == snap.snapshot_id
        assert "assessments_json" in latest.__dict__ or hasattr(latest, "assessments_json")
    finally:
        await session.close()
        await engine.dispose()


@pytest.mark.asyncio
async def test_analytics_aggregator_populated_database():
    from app.application.analytics.services.analytics_aggregator import AnalyticsAggregatorService
    from app.infrastructure.persistence.models.orm_models import AssessmentSessionORM
    from app.infrastructure.behavior.orm_models import BehaviorEvidenceORM
    from app.infrastructure.research.orm_models import ValidationDatasetORM

    engine, session = await _make_session()
    try:
        # Seed 2 Assessment Sessions
        sess1 = AssessmentSessionORM(
            candidate_id="cand-1",
            scenario_id="scenario-a",
            status="COMPLETED",
        )
        sess2 = AssessmentSessionORM(
            candidate_id="cand-2",
            scenario_id="scenario-b",
            status="INITIALIZED",
        )
        session.add_all([sess1, sess2])

        # Seed 1 Behavior Evidence record
        ev = BehaviorEvidenceORM(
            transcript_id=uuid.uuid4(),
            prompt_execution_id=uuid.uuid4(),
            candidate_id="cand-1",
            assessment_id=uuid.uuid4(),
            scenario_id=uuid.uuid4(),
            overall_confidence=0.88,
            behavior_observations=[{"construct": "CHC_Gf", "confidence": 0.9}],
            metadata_json={},
        )
        session.add(ev)

        # Seed 1 Validation Dataset record
        ds = ValidationDatasetORM(
            candidate_id="cand-1",
            assessment_id=str(uuid.uuid4()),
            scenario_id="scenario-a",
            session_id=str(uuid.uuid4()),
            status="READY",
        )
        session.add(ds)

        await session.commit()

        svc = AnalyticsAggregatorService(session)
        snap = await svc.aggregate_dashboard(TimeWindow.ALL_TIME)

        assert snap.assessments.total_assessments == 2
        assert snap.assessments.completed_assessments == 1
        assert snap.assessments.overall_completion_rate == 50.0
        assert snap.evidence.total_evidence_count == 1
        assert snap.evidence.average_quality_score == 0.88
        assert snap.research.total_validation_datasets == 1
        assert snap.research.ready_datasets == 1
    finally:
        await session.close()
        await engine.dispose()


# ---------------------------------------------------------------------------
# API Integration Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_analytics_api_endpoints(async_client):
    # 1. Dashboard
    res = await async_client.get("/api/v1/analytics/dashboard")
    assert res.status_code == 200
    body = res.json()
    assert "snapshot_id" in body
    assert "assessments" in body
    assert "frameworks" in body

    # 2. Assessments
    res = await async_client.get("/api/v1/analytics/assessments?window=weekly")
    assert res.status_code == 200
    assert "total_assessments" in res.json()

    # 3. Frameworks
    res = await async_client.get("/api/v1/analytics/frameworks")
    assert res.status_code == 200
    assert "chc" in res.json()

    # 4. Evidence
    res = await async_client.get("/api/v1/analytics/evidence")
    assert res.status_code == 200
    assert "total_evidence_count" in res.json()

    # 5. Research
    res = await async_client.get("/api/v1/analytics/research")
    assert res.status_code == 200
    assert "total_validation_datasets" in res.json()

    # 6. Platform
    res = await async_client.get("/api/v1/analytics/platform")
    assert res.status_code == 200
    assert "speech_provider_usage" in res.json()


@pytest.mark.asyncio
async def test_analytics_api_invalid_window(async_client):
    res = await async_client.get("/api/v1/analytics/dashboard?window=invalid_window")
    assert res.status_code == 400
    body = res.json()
    assert "Invalid time window" in body.get("message", body.get("detail", ""))
