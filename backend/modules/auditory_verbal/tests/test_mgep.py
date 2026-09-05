"""
MGEP Test Suite — Model Governance & Experimentation Platform (Phase 13).

Tests for:
  - Domain models & Value objects (ModelVersion, ConfigurationHash, ExperimentStatus, etc.)
  - Application Services (RegistryService, ExperimentService, ComparisonService)
  - Infrastructure Repositories (ModelRegistryRepository, ConfigurationSnapshotRepository, etc.)
  - API router endpoints (/governance/*)
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.domain.governance.value_objects.model_version import ModelVersion
from app.domain.governance.value_objects.experiment_status import ExperimentStatus
from app.domain.governance.value_objects.configuration_hash import ConfigurationHash
from app.domain.governance.entities.model_registry import RegisteredModel
from app.domain.governance.entities.configuration_snapshot import ConfigurationSnapshot
from app.domain.governance.entities.experiment import Experiment
from app.domain.governance.entities.experiment_run import ExperimentRun
from app.domain.governance.entities.comparison_report import ComparisonReport


# ---------------------------------------------------------------------------
# Domain Model Tests
# ---------------------------------------------------------------------------


class TestMGEPDomainModels:
    def test_model_version_validation(self):
        v = ModelVersion("1.0.0")
        assert str(v) == "1.0.0"

        with pytest.raises(ValueError):
            ModelVersion("")

    def test_configuration_hash_computation(self):
        cfg1 = {"a": 1, "b": "test"}
        cfg2 = {"b": "test", "a": 1}  # sorted keys match
        hash1 = ConfigurationHash.compute(cfg1)
        hash2 = ConfigurationHash.compute(cfg2)
        assert str(hash1) == str(hash2)
        assert len(str(hash1)) == 64

    def test_registered_model_lifecycle(self):
        m = RegisteredModel(
            name="SpeechModel-v1",
            category="SPEECH",
            version=ModelVersion("1.0.0"),
            owner="SpeechTeam",
            description="Deepgram Nova-2",
        )
        assert m.status == "ACTIVE"
        m.deprecate()
        assert m.status == "DEPRECATED"
        m.archive()
        assert m.status == "ARCHIVED"

    def test_registered_model_invalid_name(self):
        with pytest.raises(ValueError):
            RegisteredModel(
                name="",
                category="SPEECH",
                version=ModelVersion("1.0.0"),
                owner="Team",
            )

    def test_configuration_snapshot_auto_hash(self):
        snap = ConfigurationSnapshot(
            snapshot_name="Production Config Q3",
            created_by="Dr. Alice",
            speech_model_id="speech-001",
            llm_model_id="llm-001",
            full_config={"temperature": 0.2},
        )
        assert snap.config_hash is not None
        assert len(str(snap.config_hash)) == 64

    def test_experiment_lifecycle(self):
        exp = Experiment(
            title="Prompt Variant Comparison",
            owner="Dr. Bob",
            baseline_snapshot_id=str(uuid.uuid4()),
            candidate_snapshot_id=str(uuid.uuid4()),
        )
        assert exp.status == ExperimentStatus.DRAFT
        exp.start()
        assert exp.status == ExperimentStatus.RUNNING
        exp.complete()
        assert exp.status == ExperimentStatus.COMPLETED
        assert exp.completed_at is not None


# ---------------------------------------------------------------------------
# Database Helper
# ---------------------------------------------------------------------------


async def _make_session():
    """Helper to create a fresh in-memory SQLite database with registered tables."""
    import app.infrastructure.governance.orm_models
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
# Service & Repository Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_registry_service_and_repository():
    from app.application.governance.services.registry_service import RegistryService

    engine, session = await _make_session()
    try:
        svc = RegistryService(session)

        # 1. Register Model
        model = await svc.register_model(
            name="GPT-4o-Mini",
            category="LLM_MODEL",
            version_str="1.0.0",
            owner="AITeam",
            description="OpenAI Mini LLM",
            configuration={"temperature": 0.1, "max_tokens": 1000},
        )
        await session.commit()

        fetched = await svc.get_model_by_id(model.model_id)
        assert fetched is not None
        assert fetched.name == "GPT-4o-Mini"
        assert fetched.category == "LLM_MODEL"

        # 2. List Models
        models = await svc.list_models(category="LLM_MODEL")
        assert len(models) == 1

        # 3. Create Snapshot
        snapshot = await svc.create_snapshot(
            snapshot_name="Snapshot-01",
            created_by="Dr. Alice",
            llm_model_id=model.model_id,
            full_config={"version": "1.0.0"},
        )
        await session.commit()

        fetched_snap = await svc.get_snapshot_by_id(snapshot.snapshot_id)
        assert fetched_snap is not None
        assert fetched_snap.snapshot_name == "Snapshot-01"
    finally:
        await session.close()
        await engine.dispose()


@pytest.mark.asyncio
async def test_experiment_service_and_runs():
    from app.application.governance.services.registry_service import RegistryService
    from app.application.governance.services.experiment_service import ExperimentService

    engine, session = await _make_session()
    try:
        reg_svc = RegistryService(session)
        exp_svc = ExperimentService(session)

        # Create snapshots for baseline & candidate
        snap1 = await reg_svc.create_snapshot(
            snapshot_name="Baseline Config",
            created_by="Dr. Bob",
            full_config={"prompt_version": "v1"},
        )
        snap2 = await reg_svc.create_snapshot(
            snapshot_name="Candidate Config",
            created_by="Dr. Bob",
            full_config={"prompt_version": "v2"},
        )
        await session.commit()

        # Create Experiment
        exp = await exp_svc.create_experiment(
            title="Prompt V1 vs V2 Trial",
            owner="Dr. Bob",
            baseline_snapshot_id=snap1.snapshot_id,
            candidate_snapshot_id=snap2.snapshot_id,
            dataset_sample_ids=["ds-sample-1"],
        )
        await session.commit()

        fetched_exp = await exp_svc.get_experiment_by_id(exp.experiment_id)
        assert fetched_exp is not None
        assert fetched_exp.title == "Prompt V1 vs V2 Trial"

        # Run Experiment
        runs = await exp_svc.run_experiment(exp.experiment_id)
        await session.commit()

        assert len(runs) == 2
        run_types = {r.run_type for r in runs}
        assert "BASELINE" in run_types
        assert "CANDIDATE" in run_types
    finally:
        await session.close()
        await engine.dispose()


@pytest.mark.asyncio
async def test_comparison_service():
    from app.application.governance.services.registry_service import RegistryService
    from app.application.governance.services.experiment_service import ExperimentService
    from app.application.governance.services.comparison_service import ComparisonService

    engine, session = await _make_session()
    try:
        reg_svc = RegistryService(session)
        exp_svc = ExperimentService(session)
        comp_svc = ComparisonService(session)

        snap1 = await reg_svc.create_snapshot("Baseline", "Tester")
        snap2 = await reg_svc.create_snapshot("Candidate", "Tester")
        await session.commit()

        exp = await exp_svc.create_experiment(
            title="Comparison Trial",
            owner="Tester",
            baseline_snapshot_id=snap1.snapshot_id,
            candidate_snapshot_id=snap2.snapshot_id,
        )
        await exp_svc.run_experiment(exp.experiment_id)
        await session.commit()

        report = await comp_svc.compare_runs(exp.experiment_id)
        await session.commit()

        assert report is not None
        assert report.experiment_id == exp.experiment_id
        assert "COMPOSITE" in report.score_deltas
        assert report.latency_delta_ms != 0.0
        assert report.overall_recommendation in (
            "STABLE_IMPROVEMENT",
            "SIGNIFICANT_SCORE_CHANGE_REQUIRES_HUMAN_REVIEW",
            "PERFORMANCE_REGRESSION_HIGHER_LATENCY",
        )
    finally:
        await session.close()
        await engine.dispose()


# ---------------------------------------------------------------------------
# API Integration Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_governance_api_endpoints(async_client):
    # 1. Register Model
    res = await async_client.post(
        "/api/v1/governance/models",
        json={
            "name": "Whisper-Large-v3",
            "category": "SPEECH",
            "version": "3.0.0",
            "owner": "SpeechTeam",
            "description": "OpenAI Whisper STT Model",
            "configuration": {"language": "en"},
        },
    )
    assert res.status_code == 201
    model_data = res.json()
    model_id = model_data["model_id"]
    assert model_data["name"] == "Whisper-Large-v3"
    assert model_data["checksum"] != ""

    # 2. List Models
    res = await async_client.get("/api/v1/governance/models?category=SPEECH")
    assert res.status_code == 200
    models_list = res.json()
    assert len(models_list) >= 1

    # 3. Create Snapshots
    res_snap1 = await async_client.post(
        "/api/v1/governance/snapshots",
        json={
            "snapshot_name": "Baseline Production Snapshot",
            "created_by": "Researcher Alice",
            "speech_model_id": model_id,
        },
    )
    assert res_snap1.status_code == 201
    snap1_id = res_snap1.json()["snapshot_id"]

    res_snap2 = await async_client.post(
        "/api/v1/governance/snapshots",
        json={
            "snapshot_name": "Candidate Experimental Snapshot",
            "created_by": "Researcher Alice",
            "speech_model_id": model_id,
        },
    )
    assert res_snap2.status_code == 201
    snap2_id = res_snap2.json()["snapshot_id"]

    # 4. Create Experiment
    res_exp = await async_client.post(
        "/api/v1/governance/experiments",
        json={
            "title": "STT Model Performance Trial",
            "owner": "Researcher Alice",
            "baseline_snapshot_id": snap1_id,
            "candidate_snapshot_id": snap2_id,
            "description": "Evaluating Whisper v3 against baseline",
        },
    )
    assert res_exp.status_code == 201
    exp_data = res_exp.json()
    exp_id = exp_data["experiment_id"]
    assert exp_data["status"] == "DRAFT"

    # 5. List Experiments
    res_list_exp = await async_client.get("/api/v1/governance/experiments")
    assert res_list_exp.status_code == 200
    assert len(res_list_exp.json()) >= 1

    # 6. Execute Experiment Runs
    res_run = await async_client.post(f"/api/v1/governance/experiments/{exp_id}/run")
    assert res_run.status_code == 200
    runs_data = res_run.json()
    assert len(runs_data) == 2

    # 7. Get Experiment Details (with runs)
    res_detail = await async_client.get(f"/api/v1/governance/experiments/{exp_id}")
    assert res_detail.status_code == 200
    assert len(res_detail.json()["runs"]) == 2

    # 8. Compare Experiment Runs
    res_compare = await async_client.post(
        "/api/v1/governance/compare",
        json={"experiment_id": exp_id},
    )
    assert res_compare.status_code == 200
    report_data = res_compare.json()
    assert report_data["experiment_id"] == exp_id
    assert "score_deltas" in report_data
    assert "overall_recommendation" in report_data
