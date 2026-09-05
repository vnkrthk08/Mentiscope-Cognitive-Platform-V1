"""
PVCSF Test Suite — Psychometric Validation & Calibration Support Framework.

Tests for:
  - Domain entities (ValidationDataset, ExpertReview, CalibrationBatch, ResearchExport)
  - Value objects (ResearchMetadata, CalibrationMetadata, AgreementMetrics)
  - Application services (DatasetService, CalibrationService, ExportService)
  - Infrastructure repositories (in-memory SQLite via aiosqlite)
  - API endpoints
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio  # noqa: F401
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# ---------------------------------------------------------------------------
# Domain / Value Object Tests
# ---------------------------------------------------------------------------


class TestResearchMetadata:
    def test_valid_creation(self):
        from app.domain.research.value_objects.research_metadata import ResearchMetadata

        meta = ResearchMetadata(
            pipeline_version="2.0.0",
            model_version="gemini-1.5-pro",
            prompt_version="1.2.0",
            scoring_policy_version="1.0.0",
        )
        assert meta.pipeline_version == "2.0.0"
        assert meta.framework_version == "1.0.0"

    def test_missing_pipeline_version_raises(self):
        from app.domain.research.value_objects.research_metadata import ResearchMetadata

        with pytest.raises(ValueError, match="pipeline_version"):
            ResearchMetadata(
                pipeline_version="",
                model_version="gemini",
                prompt_version="1.0.0",
                scoring_policy_version="1.0.0",
            )

    def test_to_dict(self):
        from app.domain.research.value_objects.research_metadata import ResearchMetadata

        meta = ResearchMetadata(
            pipeline_version="1.0.0",
            model_version="gpt-4",
            prompt_version="1.0.0",
            scoring_policy_version="1.0.0",
            notes="Test run",
        )
        d = meta.to_dict()
        assert d["notes"] == "Test run"
        assert "generated_at" in d


class TestCalibrationMetadata:
    def test_valid_creation(self):
        from app.domain.research.value_objects.calibration_metadata import CalibrationMetadata

        meta = CalibrationMetadata(
            target_policy_version="1.0.0",
            calibration_round=1,
            initiated_by="Dr. Smith",
            rationale="Initial calibration run.",
        )
        assert meta.calibration_round == 1
        assert meta.calibration_tool == "PVCSF-Calibration/1.0"

    def test_invalid_round_raises(self):
        from app.domain.research.value_objects.calibration_metadata import CalibrationMetadata

        with pytest.raises(ValueError, match="calibration_round"):
            CalibrationMetadata(
                target_policy_version="1.0.0",
                calibration_round=0,
                initiated_by="Dr. A",
                rationale="Round 0 is invalid.",
            )

    def test_to_dict_structure(self):
        from app.domain.research.value_objects.calibration_metadata import CalibrationMetadata

        meta = CalibrationMetadata(
            target_policy_version="2.0.0",
            calibration_round=3,
            initiated_by="Dr. B",
            rationale="Third calibration.",
        )
        d = meta.to_dict()
        assert d["calibration_round"] == 3
        assert d["completed_at"] is None


class TestAgreementMetrics:
    def test_compute_deltas(self):
        from app.domain.research.value_objects.agreement_metrics import AgreementMetrics

        m = AgreementMetrics(
            ai_construct_scores={"fluid_reasoning": 75.0, "working_memory": 60.0},
            expert_construct_scores={"fluid_reasoning": 70.0, "working_memory": 65.0},
            reviewer_id="r-001",
        )
        deltas = m.compute_deltas()
        assert deltas["fluid_reasoning"] == 5.0
        assert deltas["working_memory"] == -5.0

    def test_empty_ai_scores_raises(self):
        from app.domain.research.value_objects.agreement_metrics import AgreementMetrics

        with pytest.raises(ValueError, match="ai_construct_scores"):
            AgreementMetrics(
                ai_construct_scores={},
                expert_construct_scores={"x": 50.0},
                reviewer_id="r-001",
            )

    def test_to_dict(self):
        from app.domain.research.value_objects.agreement_metrics import AgreementMetrics

        m = AgreementMetrics(
            ai_construct_scores={"a": 80.0},
            expert_construct_scores={"a": 75.0},
            reviewer_id="r-002",
            agreement_flag="AGREEMENT",
        )
        d = m.to_dict()
        assert d["agreement_flag"] == "AGREEMENT"


# ---------------------------------------------------------------------------
# Entity Tests
# ---------------------------------------------------------------------------


class TestValidationDataset:
    def _make_dataset(self, **kwargs):
        from app.domain.research.entities.validation_dataset import ValidationDataset

        defaults = dict(
            candidate_id="cand-001",
            assessment_id=str(uuid.uuid4()),
            scenario_id="SCN-001",
            session_id=str(uuid.uuid4()),
            transcript_text="The candidate described a logistics challenge.",
            transcript_confidence=0.95,
            behavior_evidence=[{"construct": "fluid_reasoning", "confidence": 0.85}],
            behavior_confidence=0.85,
            observation_count=3,
            construct_evaluations=[{"construct_name": "CHC_FLUID", "confidence": 0.9}],
            construct_confidence_scores={"CHC_FLUID": 0.9},
            frameworks_evaluated=["CHC"],
            ai_framework_scores={"CHC": 72.0},
            ai_composite_score=72.0,
            score_confidence=0.88,
        )
        defaults.update(kwargs)
        return ValidationDataset(**defaults)

    def test_validate_completeness_passes(self):
        ds = self._make_dataset()
        missing = ds.validate_completeness()
        assert missing == []

    def test_validate_completeness_missing_transcript(self):
        ds = self._make_dataset(transcript_text="")
        missing = ds.validate_completeness()
        assert "transcript_text" in missing

    def test_mark_ready_succeeds(self):
        ds = self._make_dataset()
        ds.mark_ready()
        assert ds.status == "READY"

    def test_mark_ready_fails_on_incomplete(self):
        ds = self._make_dataset(candidate_id="")
        with pytest.raises(ValueError, match="Missing"):
            ds.mark_ready()

    def test_mark_exported_from_ready(self):
        ds = self._make_dataset()
        ds.mark_ready()
        ds.mark_exported()
        assert ds.status == "EXPORTED"

    def test_mark_exported_from_draft_raises(self):
        ds = self._make_dataset()
        with pytest.raises(ValueError, match="READY"):
            ds.mark_exported()

    def test_apply_expert_review_approved(self):
        ds = self._make_dataset()
        ds.apply_expert_review(
            reviewer_id="psych-001",
            expert_scores={"CHC": 68.0},
            notes="Slight overestimation of fluid reasoning.",
            approved=True,
        )
        assert ds.review_status == "APPROVED"
        assert ds.expert_ratings == {"CHC": 68.0}

    def test_apply_expert_review_rejected(self):
        ds = self._make_dataset()
        ds.apply_expert_review(
            reviewer_id="psych-001",
            expert_scores={"CHC": 50.0},
            notes="Evidence insufficient.",
            approved=False,
        )
        assert ds.review_status == "REJECTED"

    def test_double_approve_raises(self):
        ds = self._make_dataset()
        ds.apply_expert_review(
            reviewer_id="p001",
            expert_scores={"CHC": 70.0},
            notes="",
            approved=True,
        )
        with pytest.raises(ValueError, match="already been approved"):
            ds.apply_expert_review(
                reviewer_id="p002",
                expert_scores={"CHC": 72.0},
                notes="",
                approved=True,
            )

    def test_to_flat_dict_keys(self):
        ds = self._make_dataset()
        flat = ds.to_flat_dict()
        assert "dataset_id" in flat
        assert "ai_composite_score" in flat
        assert "transcript_text" in flat
        assert "frameworks_evaluated" in flat


class TestExpertReview:
    def _make_review(self, **kwargs):
        from app.domain.research.entities.expert_review import ExpertReview

        defaults = dict(
            dataset_id=str(uuid.uuid4()),
            reviewer_id="psych-001",
            reviewer_name="Dr. Alice",
            expert_construct_scores={"fluid_reasoning": 70.0, "working_memory": 65.0},
            overall_score=68.0,
            comments="Good evidence quality.",
            decision="APPROVED",
        )
        defaults.update(kwargs)
        return ExpertReview(**defaults)

    def test_submit_transitions_to_submitted(self):
        r = self._make_review()
        r.submit()
        assert r.status == "SUBMITTED"
        assert r.submitted_at is not None

    def test_submit_from_non_draft_raises(self):
        r = self._make_review()
        r.submit()
        with pytest.raises(ValueError, match="DRAFT"):
            r.submit()

    def test_approve_after_submit(self):
        r = self._make_review()
        r.submit()
        r.approve()
        assert r.decision == "APPROVED"
        assert r.status == "FINALISED"

    def test_reject_requires_reason(self):
        r = self._make_review()
        r.submit()
        with pytest.raises(ValueError, match="reason"):
            r.reject("")

    def test_reject_with_reason(self):
        r = self._make_review()
        r.submit()
        r.reject("Insufficient evidence provided.")
        assert r.decision == "REJECTED"
        assert r.rejection_reason == "Insufficient evidence provided."

    def test_invalid_score_raises(self):
        from app.domain.research.entities.expert_review import ExpertReview

        r = ExpertReview(
            dataset_id="d-001",
            reviewer_id="p-001",
            expert_construct_scores={"x": 150.0},  # invalid
            overall_score=50.0,
        )
        errors = r.validate()
        assert any("150" in e or "0.0 and 100.0" in e for e in errors)

    def test_to_dict(self):
        r = self._make_review()
        d = r.to_dict()
        assert "review_id" in d
        assert "expert_construct_scores" in d


class TestCalibrationBatch:
    def _make_batch(self):
        from app.domain.research.entities.calibration_batch import CalibrationBatch
        from app.domain.research.value_objects.calibration_metadata import CalibrationMetadata

        metadata = CalibrationMetadata(
            target_policy_version="1.0.0",
            calibration_round=1,
            initiated_by="Dr. Jones",
            rationale="First calibration.",
        )
        return CalibrationBatch(
            batch_name="Round 1",
            metadata=metadata,
            policy_version_before="1.0.0",
        )

    def test_add_dataset(self):
        batch = self._make_batch()
        batch.add_dataset("ds-001")
        assert "ds-001" in batch.dataset_ids

    def test_no_duplicate_datasets(self):
        batch = self._make_batch()
        batch.add_dataset("ds-001")
        batch.add_dataset("ds-001")
        assert batch.dataset_ids.count("ds-001") == 1

    def test_add_dataset_to_non_open_raises(self):
        batch = self._make_batch()
        batch.status = "COMPLETED"
        with pytest.raises(ValueError, match="COMPLETED"):
            batch.add_dataset("ds-002")

    def test_add_recommendation(self):
        batch = self._make_batch()
        batch.add_recommendation("CHC", "fluid_reasoning", 2.5)
        assert batch.recommended_adjustments["CHC"]["fluid_reasoning"] == 2.5

    def test_complete_computes_summary(self):
        from app.domain.research.value_objects.agreement_metrics import AgreementMetrics

        batch = self._make_batch()
        batch.add_dataset("ds-001")

        metrics = AgreementMetrics(
            ai_construct_scores={"fluid": 80.0},
            expert_construct_scores={"fluid": 70.0},
            reviewer_id="p-001",
            score_deltas={"fluid": 10.0},
            discrepant_constructs=["fluid"],
            agreement_flag="DISCREPANT",
        )
        batch.record_agreement(metrics)
        batch.complete()
        assert batch.status == "COMPLETED"
        assert batch.reviewed_dataset_count == 1
        assert "fluid" in batch.mean_absolute_delta_per_construct

    def test_complete_from_wrong_status_raises(self):
        batch = self._make_batch()
        batch.status = "CLOSED"
        with pytest.raises(ValueError, match="OPEN"):
            batch.complete()

    def test_to_dict(self):
        batch = self._make_batch()
        d = batch.to_dict()
        assert "batch_id" in d
        assert "recommended_adjustments" in d


class TestResearchExport:
    def _make_export(self):
        from app.domain.research.entities.research_export import ResearchExport

        return ResearchExport(
            export_name="Test Export",
            dataset_ids=["ds-001", "ds-002"],
            export_format="CSV",
            requested_by="researcher-001",
        )

    def test_lifecycle_pending_to_completed(self):
        export = self._make_export()
        assert export.status == "PENDING"
        export.mark_in_progress()
        assert export.status == "IN_PROGRESS"
        export.mark_completed(
            file_path="/exports/test.csv",
            file_size_bytes=4096,
            record_count=2,
            checksum="abc123",
        )
        assert export.status == "COMPLETED"
        assert export.file_path == "/exports/test.csv"
        assert export.record_count == 2

    def test_mark_in_progress_from_wrong_state(self):
        export = self._make_export()
        export.status = "COMPLETED"
        with pytest.raises(ValueError, match="PENDING"):
            export.mark_in_progress()

    def test_mark_failed(self):
        export = self._make_export()
        export.mark_in_progress()
        export.mark_failed("Disk full.")
        assert export.status == "FAILED"
        assert export.error_message == "Disk full."

    def test_to_dict(self):
        export = self._make_export()
        d = export.to_dict()
        assert "export_id" in d
        assert d["export_format"] == "CSV"


# ---------------------------------------------------------------------------
# Application Service Tests
# ---------------------------------------------------------------------------


class TestCalibrationServiceUnit:
    """Unit tests for CalibrationService (no DB)."""

    def _svc(self):
        from app.application.research.services.calibration_service import CalibrationService

        return CalibrationService(session=MagicMock())

    def test_create_batch(self):
        svc = self._svc()
        batch = svc.create_batch(
            batch_name="Test Batch",
            target_policy_version="1.0.0",
            calibration_round=1,
            initiated_by="Dr. Test",
            rationale="Test calibration run for policy v1.0.0.",
        )
        assert batch.batch_name == "Test Batch"
        assert batch.metadata is not None
        assert batch.status == "OPEN"

    def test_build_expert_review(self):
        svc = self._svc()
        review = svc.build_expert_review(
            dataset_id="ds-001",
            reviewer_id="psych-001",
            reviewer_name="Dr. Jane",
            reviewer_credentials="PhD Psychology",
            expert_scores={"CHC": 70.0},
            overall_score=70.0,
            comments="Accurate.",
            strengths=["Clear evidence"],
            concerns=[],
            recommendations=[],
            approved=True,
        )
        assert review.reviewer_name == "Dr. Jane"
        assert review.decision == "APPROVED"

    def test_process_expert_review_agreement(self):
        svc = self._svc()
        batch = svc.create_batch(
            batch_name="B1",
            target_policy_version="1.0.0",
            calibration_round=1,
            initiated_by="p-001",
            rationale="Testing.",
        )
        review = svc.build_expert_review(
            dataset_id="ds-001",
            reviewer_id="p-001",
            reviewer_name="Dr. X",
            reviewer_credentials="PhD",
            expert_scores={"CHC": 70.0},
            overall_score=70.0,
            comments="",
            strengths=[],
            concerns=[],
            recommendations=[],
            approved=True,
        )
        ai_scores = {"CHC": 72.0}
        metrics = svc.process_expert_review(batch, review, ai_scores)
        assert metrics.agreement_flag in ("AGREEMENT", "PARTIAL", "DISCREPANT")
        assert batch.status == "IN_PROGRESS"

    def test_add_recommendation(self):
        svc = self._svc()
        batch = svc.create_batch(
            batch_name="B2",
            target_policy_version="1.0.0",
            calibration_round=2,
            initiated_by="p-001",
            rationale="Second round.",
        )
        svc.add_recommendation(batch, "CHC", "fluid_reasoning", 2.5, "Mean delta > 5 points")
        assert batch.recommended_adjustments["CHC"]["fluid_reasoning"] == 2.5


# ---------------------------------------------------------------------------
# Infrastructure ORM / Repository Tests
# ---------------------------------------------------------------------------
# These tests each create their own isolated in-memory engine so they do
# not rely on the session-scoped conftest engine, avoiding scope mismatches.
# ---------------------------------------------------------------------------


async def _make_session():
    """Helper: create a fresh in-memory SQLite engine + session for one test."""
    import app.infrastructure.research.orm_models  # ensure PVCSF tables registered
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


@pytest.mark.asyncio
async def test_validation_dataset_repo_save_and_fetch():
    from app.domain.research.entities.validation_dataset import ValidationDataset
    from app.domain.research.value_objects.research_metadata import ResearchMetadata
    from app.infrastructure.research.repositories import ValidationDatasetRepository

    engine, session = await _make_session()
    try:
        meta = ResearchMetadata(
            pipeline_version="1.0.0",
            model_version="gemini-1.5-pro",
            prompt_version="1.0.0",
            scoring_policy_version="1.0.0",
        )
        ds = ValidationDataset(
            candidate_id="cand-001",
            assessment_id=str(uuid.uuid4()),
            scenario_id="SCN-001",
            session_id=str(uuid.uuid4()),
            transcript_text="Test transcript.",
            transcript_confidence=0.90,
            behavior_evidence=[{"construct": "CHC"}],
            behavior_confidence=0.85,
            observation_count=2,
            construct_evaluations=[{"name": "CHC"}],
            frameworks_evaluated=["CHC"],
            ai_framework_scores={"CHC": 70.0},
            ai_composite_score=70.0,
            score_confidence=0.88,
            metadata=meta,
        )
        ds.status = "READY"

        repo = ValidationDatasetRepository(session)
        await repo.save(ds)
        await session.commit()

        fetched = await repo.get_by_id(ds.dataset_id)
        assert fetched is not None
        assert fetched.candidate_id == "cand-001"
        assert fetched.status == "READY"
        assert fetched.metadata is not None
        assert fetched.metadata.pipeline_version == "1.0.0"
    finally:
        await session.close()
        await engine.dispose()


@pytest.mark.asyncio
async def test_expert_review_repo_save_and_list():
    from app.domain.research.entities.expert_review import ExpertReview
    from app.infrastructure.research.repositories import ExpertReviewRepository

    engine, session = await _make_session()
    try:
        dataset_id = str(uuid.uuid4())
        review = ExpertReview(
            dataset_id=dataset_id,
            reviewer_id="psych-001",
            reviewer_name="Dr. Test",
            expert_construct_scores={"CHC": 68.0},
            overall_score=68.0,
            comments="Accurate.",
            decision="APPROVED",
            status="SUBMITTED",
            submitted_at=datetime.now(timezone.utc),
        )

        repo = ExpertReviewRepository(session)
        await repo.save(review)
        await session.commit()

        reviews = await repo.list_by_dataset(dataset_id)
        assert len(reviews) == 1
        assert reviews[0].reviewer_id == "psych-001"
    finally:
        await session.close()
        await engine.dispose()


@pytest.mark.asyncio
async def test_calibration_batch_repo_save_and_fetch():
    from app.domain.research.entities.calibration_batch import CalibrationBatch
    from app.domain.research.value_objects.calibration_metadata import CalibrationMetadata
    from app.infrastructure.research.repositories import CalibrationBatchRepository

    engine, session = await _make_session()
    try:
        meta = CalibrationMetadata(
            target_policy_version="1.0.0",
            calibration_round=1,
            initiated_by="Dr. Admin",
            rationale="Initial calibration.",
        )
        batch = CalibrationBatch(
            batch_name="Round 1",
            metadata=meta,
            dataset_ids=["ds-001", "ds-002"],
            policy_version_before="1.0.0",
        )

        repo = CalibrationBatchRepository(session)
        await repo.save(batch)
        await session.commit()

        fetched = await repo.get_by_id(batch.batch_id)
        assert fetched is not None
        assert fetched.batch_name == "Round 1"
        assert "ds-001" in fetched.dataset_ids

        open_count = await repo.count_open()
        assert open_count == 1
    finally:
        await session.close()
        await engine.dispose()


@pytest.mark.asyncio
async def test_research_export_repo_save_and_list():
    from app.domain.research.entities.research_export import ResearchExport
    from app.infrastructure.research.repositories import ResearchExportRepository

    engine, session = await _make_session()
    try:
        export = ResearchExport(
            export_name="CSV Export",
            dataset_ids=["ds-001"],
            export_format="CSV",
            requested_by="researcher-001",
            status="COMPLETED",
            file_path="/exports/test.csv",
            file_size_bytes=2048,
            record_count=1,
        )

        repo = ResearchExportRepository(session)
        await repo.save(export)
        await session.commit()

        exports = await repo.list_all()
        assert len(exports) >= 1
        assert exports[0].export_format == "CSV"

        total = await repo.count()
        assert total == 1

        by_format = await repo.count_by_format()
        assert "CSV" in by_format
        assert by_format["CSV"] == 1
    finally:
        await session.close()
        await engine.dispose()


@pytest.mark.asyncio
async def test_dataset_repo_list_by_status():
    from app.domain.research.entities.validation_dataset import ValidationDataset
    from app.infrastructure.research.repositories import ValidationDatasetRepository

    engine, session = await _make_session()
    try:
        repo = ValidationDatasetRepository(session)

        for i in range(3):
            ds = ValidationDataset(
                candidate_id=f"cand-{i}",
                assessment_id=str(uuid.uuid4()),
                scenario_id="SCN-001",
                session_id=str(uuid.uuid4()),
                status="READY" if i < 2 else "DRAFT",
            )
            await repo.save(ds)
        await session.commit()

        ready = await repo.list_all(status="READY")
        assert len(ready) == 2

        total = await repo.count()
        assert total == 3
    finally:
        await session.close()
        await engine.dispose()


@pytest.mark.asyncio
async def test_pvcsf_metrics_record():
    from app.infrastructure.research.metrics import PVCSFMetrics
    from app.infrastructure.research.orm_models import PVCSFMetricORM
    from sqlalchemy import select

    engine, session = await _make_session()
    try:
        metrics = PVCSFMetrics(session)
        await metrics.record_dataset_generated(
            dataset_id=str(uuid.uuid4()),
            elapsed_ms=123.4,
            candidate_id="cand-001",
            status="READY",
        )
        await metrics.record_export_completed(
            export_id=str(uuid.uuid4()),
            export_format="JSON",
            record_count=5,
            file_size_bytes=10240,
        )
        await session.commit()

        result = await session.execute(select(PVCSFMetricORM))
        rows = result.scalars().all()
        assert len(rows) == 2
        metric_types = {r.metric_type for r in rows}
        assert "DATASET_GENERATED" in metric_types
        assert "EXPORT_COMPLETED" in metric_types
    finally:
        await session.close()
        await engine.dispose()


# ---------------------------------------------------------------------------
# Exporter Tests (with temp directory)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_csv_exporter(tmp_path):
    from app.domain.research.entities.validation_dataset import ValidationDataset
    from app.infrastructure.research.exporters.csv_exporter import CSVExporter

    datasets = [
        ValidationDataset(
            candidate_id="cand-001",
            assessment_id="asmnt-001",
            scenario_id="SCN-001",
            session_id="sess-001",
            transcript_text="Hello world.",
            ai_framework_scores={"CHC": 70.0},
            ai_composite_score=70.0,
        )
    ]

    exporter = CSVExporter(str(tmp_path))
    file_path, file_size, checksum = await exporter.write(
        export_id="test-export-001",
        datasets=datasets,
    )

    assert file_path.exists()
    assert file_size > 0
    assert checksum is not None and len(checksum) == 64

    import pandas as pd
    df = pd.read_csv(file_path)
    assert len(df) == 1
    assert "dataset_id" in df.columns
    assert "ai_composite_score" in df.columns


@pytest.mark.asyncio
async def test_json_exporter(tmp_path):
    import json

    from app.domain.research.entities.validation_dataset import ValidationDataset
    from app.infrastructure.research.exporters.json_exporter import JSONExporter

    datasets = [
        ValidationDataset(
            candidate_id="cand-001",
            assessment_id="asmnt-001",
            scenario_id="SCN-001",
            session_id="sess-001",
            transcript_text="Test.",
            ai_framework_scores={"RIASEC": 65.0},
            ai_composite_score=65.0,
        )
    ]

    exporter = JSONExporter(str(tmp_path))
    file_path, file_size, checksum = await exporter.write(
        export_id="json-export-001",
        datasets=datasets,
    )

    assert file_path.exists()
    with open(file_path) as f:
        data = json.load(f)
    assert data["record_count"] == 1
    assert len(data["datasets"]) == 1
    assert data["datasets"][0]["candidate_id"] == "cand-001"


@pytest.mark.asyncio
async def test_excel_exporter(tmp_path):
    import pandas as pd

    from app.domain.research.entities.validation_dataset import ValidationDataset
    from app.infrastructure.research.exporters.excel_exporter import ExcelExporter

    datasets = [
        ValidationDataset(
            candidate_id="cand-002",
            assessment_id="asmnt-002",
            scenario_id="SCN-002",
            session_id="sess-002",
            transcript_text="Excel test.",
            behavior_evidence=[{
                "construct": "CHC", "confidence": 0.9,
                "quote": "Q", "indicator": "I",
                "polarity": "+", "evidence_type": "VERBATIM",
            }],
            ai_framework_scores={"CHC": 75.0, "RIASEC": 60.0},
            ai_composite_score=67.5,
            expert_ratings={"CHC": 72.0},
        )
    ]

    exporter = ExcelExporter(str(tmp_path))
    file_path, file_size, checksum = await exporter.write(
        export_id="excel-export-001",
        datasets=datasets,
    )

    assert file_path.exists()
    xl = pd.ExcelFile(str(file_path))
    assert "Datasets" in xl.sheet_names
    assert "ConstructScores" in xl.sheet_names
    assert "BehaviorEvidence" in xl.sheet_names
    assert "ExportMetadata" in xl.sheet_names
