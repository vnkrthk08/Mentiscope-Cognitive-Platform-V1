"""
PVCSF Research API — v1 Router.

Provides REST endpoints for the Psychometric Validation &
Calibration Support Framework.

All endpoints are read/write for research data only.
NO assessment scores or pipeline results are modified.

Routes:
  POST   /research/dataset/build           Build a ValidationDataset
  GET    /research/datasets                 List all datasets
  GET    /research/datasets/{id}            Get a dataset by ID
  POST   /research/review                   Submit an expert review
  GET    /research/reviews/{dataset_id}     List reviews for a dataset
  POST   /research/calibration/create       Create a calibration batch
  POST   /research/calibration/{id}/complete  Complete a calibration batch
  POST   /research/calibration/{id}/recommend  Add score recommendation
  GET    /research/calibration/{id}          Get a calibration batch
  GET    /research/calibrations             List all calibration batches
  POST   /research/exports                  Create and run an export job
  GET    /research/exports/{id}             Get export job status/details
  GET    /research/exports                  List recent exports
  GET    /research/metrics                  PVCSF operational metrics
  GET    /research/dashboard                Existing RAVMF dashboard (preserved)
  GET    /research/validation               Existing validation status (preserved)
  GET    /research/experiments              Existing experiments (preserved)
"""
from __future__ import annotations

import time
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.research.dto import (
    AddRecommendationRequest,
    BuildDatasetRequest,
    CalibrationBatchResponse,
    CreateCalibrationRequest,
    CreateExportRequest,
    DatasetListResponse,
    ExpertReviewRequest,
    ExpertReviewResponse,
    ExportResponse,
    ResearchMetricsSummary,
    ValidationDatasetResponse,
)
from app.application.research.services.calibration_service import CalibrationService
from app.application.research.services.dataset_service import DatasetService
from app.application.research.services.export_service import ExportService
from app.core.logging import logger
from app.infrastructure.persistence.database.session import AsyncSessionLocal
from app.infrastructure.research.metrics import PVCSFMetrics
from app.infrastructure.research.orm_models import (
    CalibrationBatchORM,
    ResearchExportORM,
    ValidationDatasetORM,
)
from app.infrastructure.research.repositories import (
    CalibrationBatchRepository,
    ExpertReviewRepository,
    ResearchExportRepository,
    ValidationDatasetRepository,
)

router = APIRouter(prefix="/research", tags=["Research & Analytics Framework"])


# ---------------------------------------------------------------------------
# Dependency: shared async session
# ---------------------------------------------------------------------------

async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


# ---------------------------------------------------------------------------
# Existing RAVMF endpoints (preserved — do NOT remove or modify)
# ---------------------------------------------------------------------------

def get_research_framework(request: Request):
    return request.app.state.platform_manager.registry.get_subsystem(
        "ResearchAnalyticsFramework"
    )


@router.get(
    "/dashboard",
    summary="Get Research Dashboard Snapshot",
    description="Loads a real-time snapshot model representing platform quality, research, analytics, and operational health.",
)
async def get_research_dashboard(
    framework=Depends(get_research_framework),
):
    try:
        from app.infrastructure.persistence.database.unit_of_work import UnitOfWork

        dashboard = await framework.generate_research_dashboard()
        async with UnitOfWork() as uow:
            await uow.research.save_snapshot(dashboard)
            await uow.commit()

        return {
            "snapshot_id": dashboard.snapshot_id,
            "research_metrics": dashboard.research_metrics,
            "analytics_metrics": dashboard.analytics_metrics,
            "validation_metrics": {
                "reliability_status": dashboard.validation_metrics.reliability_status if dashboard.validation_metrics else "STABLE (0.92)",
                "calibration_status": dashboard.validation_metrics.calibration_status if dashboard.validation_metrics else "CALIBRATED",
                "drift_status": dashboard.validation_metrics.drift_status if dashboard.validation_metrics else "NO_DRIFT_DETECTED",
                "norm_status": dashboard.validation_metrics.norm_status if dashboard.validation_metrics else "VALIDATED",
            },
            "monitoring_metrics": {
                "health_status": dashboard.monitoring_metrics.health_status if dashboard.monitoring_metrics else "HEALTHY",
                "latency": dashboard.monitoring_metrics.latency if dashboard.monitoring_metrics else {},
            },
            "experiments_count": len(dashboard.experiment_results),
            "platform_metadata": dashboard.platform_metadata,
            "created_at": dashboard.created_at.isoformat(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate dashboard: {str(e)}",
        )


@router.get(
    "/validation",
    summary="Get Psychometric Validation Status",
    description="Returns detailed validation parameters, drift warning logs, and calibration quality.",
)
async def get_validation_status(
    framework=Depends(get_research_framework),
):
    dashboard = await framework.generate_research_dashboard()
    v = dashboard.validation_metrics
    return {
        "reliability_status": v.reliability_status if v else "STABLE (0.92)",
        "calibration_status": v.calibration_status if v else "CALIBRATED",
        "drift_status": v.drift_status if v else "NO_DRIFT_DETECTED",
        "norm_status": v.norm_status if v else "VALIDATED",
        "warnings": v.warnings if v else [],
        "recommendations": v.recommendations if v else [],
    }


@router.get(
    "/experiments",
    summary="Get Active Experiments",
    description="Lists configurations and outcome statuses for active psychometric A/B trials.",
)
async def get_experiments(
    framework=Depends(get_research_framework),
):
    dashboard = await framework.generate_research_dashboard()
    return [
        {
            "experiment_id": exp.experiment_id,
            "experiment_type": exp.experiment_type,
            "configuration": exp.configuration,
            "outcome": exp.outcome,
            "metrics": exp.metrics,
            "winner": exp.winner,
            "metadata": exp.metadata,
        }
        for exp in dashboard.experiment_results
    ]


# ---------------------------------------------------------------------------
# PVCSF: Dataset endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/dataset/build",
    response_model=ValidationDatasetResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Build Validation Dataset",
    description=(
        "Builds a ValidationDataset record from a completed assessment pipeline run. "
        "Aggregates transcripts, behavioral evidence, construct evaluations, and assessment "
        "scores into a single exportable research record. "
        "DOES NOT modify any assessment results."
    ),
)
async def build_dataset(
    req: BuildDatasetRequest,
    session: AsyncSession = Depends(get_session),
):
    start_ms = time.monotonic() * 1000
    svc = DatasetService(session)
    metrics = PVCSFMetrics(session)
    repo = ValidationDatasetRepository(session)

    try:
        dataset = await svc.build_dataset(
            candidate_id=req.candidate_id,
            assessment_id=req.assessment_id,
            session_id=req.session_id,
            scenario_id=req.scenario_id,
            pipeline_version=req.pipeline_version,
            model_version=req.model_version,
            prompt_version=req.prompt_version,
            scoring_policy_version=req.scoring_policy_version,
            notes=req.notes,
        )

        await repo.save(dataset)

        elapsed_ms = (time.monotonic() * 1000) - start_ms
        await metrics.record_dataset_generated(
            dataset_id=dataset.dataset_id,
            elapsed_ms=elapsed_ms,
            candidate_id=dataset.candidate_id,
            status=dataset.status,
        )

        await session.commit()
        logger.info(f"[PVCSF API] Dataset built: {dataset.dataset_id}")
        return _to_dataset_response(dataset)

    except Exception as exc:
        await session.rollback()
        logger.error(f"[PVCSF API] Dataset build failed: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dataset build failed: {str(exc)}",
        )


@router.get(
    "/datasets",
    response_model=DatasetListResponse,
    summary="List Validation Datasets",
    description="Returns a paginated list of all ValidationDatasets with optional filters.",
)
async def list_datasets(
    candidate_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    repo = ValidationDatasetRepository(session)
    offset = (page - 1) * page_size
    datasets = await repo.list_all(
        candidate_id=candidate_id,
        status=status_filter,
        limit=page_size,
        offset=offset,
    )
    total = await repo.count(status=status_filter)
    return DatasetListResponse(
        datasets=[_to_dataset_response(ds) for ds in datasets],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/datasets/{dataset_id}",
    response_model=ValidationDatasetResponse,
    summary="Get Validation Dataset",
    description="Retrieves a single ValidationDataset by ID.",
)
async def get_dataset(
    dataset_id: str,
    session: AsyncSession = Depends(get_session),
):
    repo = ValidationDatasetRepository(session)
    dataset = await repo.get_by_id(dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset '{dataset_id}' not found.",
        )
    return _to_dataset_response(dataset)


# ---------------------------------------------------------------------------
# PVCSF: Expert Review endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/review",
    response_model=ExpertReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit Expert Review",
    description=(
        "Allows a psychologist to submit a manual review of a ValidationDataset. "
        "Records expert construct scores, qualitative notes, and approval decision. "
        "Does NOT modify AI-generated assessment scores."
    ),
)
async def submit_expert_review(
    req: ExpertReviewRequest,
    session: AsyncSession = Depends(get_session),
):
    dataset_repo = ValidationDatasetRepository(session)
    review_repo = ExpertReviewRepository(session)
    cal_svc = CalibrationService(session)
    metrics = PVCSFMetrics(session)

    # Validate dataset exists
    dataset = await dataset_repo.get_by_id(req.dataset_id)
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset '{req.dataset_id}' not found.",
        )

    try:
        review = cal_svc.build_expert_review(
            dataset_id=req.dataset_id,
            reviewer_id=req.reviewer_id,
            reviewer_name=req.reviewer_name,
            reviewer_credentials=req.reviewer_credentials,
            expert_scores=req.expert_construct_scores,
            overall_score=req.overall_score,
            comments=req.comments,
            strengths=req.strengths,
            concerns=req.concerns,
            recommendations=req.recommendations,
            approved=req.approved,
            rejection_reason=req.rejection_reason,
            annotation_tags=req.annotation_tags,
            review_round=req.review_round,
            review_duration_minutes=req.review_duration_minutes,
        )

        # Apply review to dataset
        dataset.apply_expert_review(
            reviewer_id=req.reviewer_id,
            expert_scores=req.expert_construct_scores,
            notes=req.comments,
            approved=req.approved,
        )

        # Persist review and updated dataset
        await review_repo.save(review)
        await dataset_repo.save(dataset)

        await metrics.record_expert_review(
            review_id=review.review_id,
            dataset_id=review.dataset_id,
            decision=review.decision,
            review_round=review.review_round,
        )

        await session.commit()
        logger.info(f"[PVCSF API] Expert review submitted: {review.review_id}")
        return _to_review_response(review)

    except Exception as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Expert review submission failed: {str(exc)}",
        )


@router.get(
    "/reviews/{dataset_id}",
    response_model=List[ExpertReviewResponse],
    summary="List Expert Reviews for Dataset",
    description="Returns all expert reviews associated with a given ValidationDataset.",
)
async def list_reviews(
    dataset_id: str,
    session: AsyncSession = Depends(get_session),
):
    repo = ExpertReviewRepository(session)
    reviews = await repo.list_by_dataset(dataset_id)
    return [_to_review_response(r) for r in reviews]


# ---------------------------------------------------------------------------
# PVCSF: Calibration endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/calibration/create",
    response_model=CalibrationBatchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Calibration Batch",
    description=(
        "Opens a new calibration batch for a specified scoring policy version. "
        "Calibration batches track inter-rater agreement and score adjustment "
        "recommendations. No automatic score changes are applied."
    ),
)
async def create_calibration_batch(
    req: CreateCalibrationRequest,
    session: AsyncSession = Depends(get_session),
):
    svc = CalibrationService(session)
    repo = CalibrationBatchRepository(session)
    metrics = PVCSFMetrics(session)

    try:
        batch = svc.create_batch(
            batch_name=req.batch_name,
            target_policy_version=req.target_policy_version,
            calibration_round=req.calibration_round,
            initiated_by=req.initiated_by,
            rationale=req.rationale,
            dataset_ids=req.dataset_ids,
            notes=req.notes,
        )

        await repo.save(batch)
        await metrics.record_calibration_batch(
            batch_id=batch.batch_id,
            status=batch.status,
            total_discrepancies=0,
            reviewed_count=0,
        )
        await session.commit()

        logger.info(f"[PVCSF API] Calibration batch created: {batch.batch_id}")
        return _to_calibration_response(batch)

    except Exception as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Calibration batch creation failed: {str(exc)}",
        )


@router.post(
    "/calibration/{batch_id}/complete",
    response_model=CalibrationBatchResponse,
    summary="Complete Calibration Batch",
    description="Marks a calibration batch as completed, computing discrepancy summary statistics.",
)
async def complete_calibration_batch(
    batch_id: str,
    session: AsyncSession = Depends(get_session),
):
    repo = CalibrationBatchRepository(session)
    svc = CalibrationService(session)
    metrics = PVCSFMetrics(session)

    batch = await repo.get_by_id(batch_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Calibration batch '{batch_id}' not found.",
        )

    try:
        svc.complete_batch(batch)
        await repo.save(batch)
        await metrics.record_calibration_batch(
            batch_id=batch.batch_id,
            status=batch.status,
            total_discrepancies=batch.total_discrepancies,
            reviewed_count=batch.reviewed_dataset_count,
        )
        await session.commit()
        return _to_calibration_response(batch)

    except (ValueError, Exception) as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )


@router.post(
    "/calibration/{batch_id}/recommend",
    response_model=CalibrationBatchResponse,
    summary="Add Score Adjustment Recommendation",
    description=(
        "Records an advisory score adjustment recommendation for a specific construct "
        "within a calibration batch. Recommendations are stored for researcher review "
        "and are NEVER automatically applied to scoring policies."
    ),
)
async def add_recommendation(
    batch_id: str,
    req: AddRecommendationRequest,
    session: AsyncSession = Depends(get_session),
):
    repo = CalibrationBatchRepository(session)
    svc = CalibrationService(session)

    batch = await repo.get_by_id(batch_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Calibration batch '{batch_id}' not found.",
        )

    svc.add_recommendation(
        batch=batch,
        framework=req.framework,
        construct=req.construct_name,
        delta=req.delta,
        justification=req.justification,
    )

    await repo.save(batch)
    await session.commit()
    return _to_calibration_response(batch)


@router.get(
    "/calibration/{batch_id}",
    response_model=CalibrationBatchResponse,
    summary="Get Calibration Batch",
    description="Retrieves a calibration batch by ID including discrepancy summary.",
)
async def get_calibration_batch(
    batch_id: str,
    session: AsyncSession = Depends(get_session),
):
    repo = CalibrationBatchRepository(session)
    batch = await repo.get_by_id(batch_id)
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Calibration batch '{batch_id}' not found.",
        )
    return _to_calibration_response(batch)


@router.get(
    "/calibrations",
    response_model=List[CalibrationBatchResponse],
    summary="List Calibration Batches",
    description="Lists all calibration batches with optional status filter.",
)
async def list_calibrations(
    status_filter: Optional[str] = Query(None, alias="status"),
    session: AsyncSession = Depends(get_session),
):
    repo = CalibrationBatchRepository(session)
    batches = await repo.list_all(status=status_filter)
    return [_to_calibration_response(b) for b in batches]


# ---------------------------------------------------------------------------
# PVCSF: Export endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/exports",
    response_model=ExportResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Research Export",
    description=(
        "Generates a research dataset export in CSV, JSON, or Excel format. "
        "Each export preserves full traceability: evidence references, "
        "construct mappings, and framework scores. "
        "Exports are saved to the server's exports/research directory."
    ),
)
async def create_export(
    req: CreateExportRequest,
    session: AsyncSession = Depends(get_session),
):
    export_svc = ExportService(session)
    dataset_repo = ValidationDatasetRepository(session)
    export_repo = ResearchExportRepository(session)
    metrics = PVCSFMetrics(session)

    try:
        # Resolve datasets
        if req.dataset_ids:
            datasets = await dataset_repo.get_by_ids(req.dataset_ids)
        elif req.calibration_batch_id:
            cal_repo = CalibrationBatchRepository(session)
            batch = await cal_repo.get_by_id(req.calibration_batch_id)
            if not batch:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Calibration batch '{req.calibration_batch_id}' not found.",
                )
            datasets = await dataset_repo.get_by_ids(batch.dataset_ids)
        else:
            # Export all READY datasets
            datasets = await dataset_repo.list_all(status="READY", limit=1000)

        if not datasets:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No READY datasets found for export.",
            )

        # Create and execute export
        export_job = export_svc.create_export_job(
            export_name=req.export_name,
            export_format=req.export_format,
            dataset_ids=[ds.dataset_id for ds in datasets],
            requested_by=req.requested_by,
            calibration_batch_id=req.calibration_batch_id,
            include_evidence=req.include_evidence,
            include_transcripts=req.include_transcripts,
            include_expert_reviews=req.include_expert_reviews,
            include_construct_mappings=req.include_construct_mappings,
        )

        # Save pending job first
        await export_repo.save(export_job)

        # Execute the actual file write
        export_job = await export_svc.execute_export(export_job, datasets)

        # Update datasets and save completed job
        for ds in datasets:
            await dataset_repo.save(ds)
        await export_repo.save(export_job)

        await metrics.record_export_completed(
            export_id=export_job.export_id,
            export_format=export_job.export_format,
            record_count=export_job.record_count,
            file_size_bytes=export_job.file_size_bytes,
        )

        await session.commit()
        logger.info(f"[PVCSF API] Export completed: {export_job.export_id}")
        return _to_export_response(export_job)

    except HTTPException:
        raise
    except Exception as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(exc)}",
        )


@router.get(
    "/exports/{export_id}",
    response_model=ExportResponse,
    summary="Get Export Job",
    description="Retrieves export job status and file details by ID.",
)
async def get_export(
    export_id: str,
    session: AsyncSession = Depends(get_session),
):
    repo = ResearchExportRepository(session)
    export = await repo.get_by_id(export_id)
    if not export:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Export '{export_id}' not found.",
        )
    return _to_export_response(export)


@router.get(
    "/exports",
    response_model=List[ExportResponse],
    summary="List Export Jobs",
    description="Returns the most recent export jobs.",
)
async def list_exports(
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    repo = ResearchExportRepository(session)
    exports = await repo.list_all(limit=limit)
    return [_to_export_response(e) for e in exports]


# ---------------------------------------------------------------------------
# PVCSF: Metrics endpoint
# ---------------------------------------------------------------------------

@router.get(
    "/metrics",
    response_model=ResearchMetricsSummary,
    summary="PVCSF Operational Metrics",
    description="Returns aggregate operational metrics for the PVCSF module.",
)
async def get_pvcsf_metrics(
    session: AsyncSession = Depends(get_session),
):
    dataset_repo = ValidationDatasetRepository(session)
    review_repo = ExpertReviewRepository(session)
    cal_repo = CalibrationBatchRepository(session)
    export_repo = ResearchExportRepository(session)

    from sqlalchemy import select, func
    from app.infrastructure.research.orm_models import ResearchExportORM

    total_ds = await dataset_repo.count()
    ready_ds = await dataset_repo.count(status="READY")
    exported_ds = await dataset_repo.count(status="EXPORTED")
    pending_reviews = await review_repo.count_pending()
    approved_reviews = await review_repo.count_approved()
    open_batches = await cal_repo.count_open()
    completed_batches = await cal_repo.count_completed()
    total_exports = await export_repo.count()
    export_by_format = await export_repo.count_by_format()

    # Compute average dataset generation time from metrics table
    from app.infrastructure.research.orm_models import PVCSFMetricORM
    from sqlalchemy import select, func as sqlfunc
    result = await session.execute(
        select(sqlfunc.avg(PVCSFMetricORM.value_json["elapsed_ms"].as_float())).where(
            PVCSFMetricORM.metric_type == "DATASET_GENERATED"
        )
    )
    avg_ms = result.scalar_one_or_none() or 0.0

    # Last export timestamp
    last_export_result = await session.execute(
        select(ResearchExportORM.completed_at)
        .where(ResearchExportORM.status == "COMPLETED")
        .order_by(ResearchExportORM.completed_at.desc())
        .limit(1)
    )
    last_export_at = last_export_result.scalar_one_or_none()

    return ResearchMetricsSummary(
        total_datasets=total_ds,
        ready_datasets=ready_ds,
        exported_datasets=exported_ds,
        pending_reviews=pending_reviews,
        approved_reviews=approved_reviews,
        open_calibration_batches=open_batches,
        completed_calibration_batches=completed_batches,
        total_exports=total_exports,
        export_by_format=export_by_format,
        dataset_generation_time_avg_ms=round(avg_ms, 2),
        last_export_at=last_export_at,
    )


# ---------------------------------------------------------------------------
# Mapping helpers
# ---------------------------------------------------------------------------

def _to_dataset_response(ds) -> ValidationDatasetResponse:
    return ValidationDatasetResponse(
        dataset_id=ds.dataset_id,
        candidate_id=ds.candidate_id,
        assessment_id=ds.assessment_id,
        scenario_id=ds.scenario_id,
        session_id=ds.session_id,
        transcript_text=ds.transcript_text,
        transcript_confidence=ds.transcript_confidence,
        observation_count=ds.observation_count,
        behavior_confidence=ds.behavior_confidence,
        frameworks_evaluated=ds.frameworks_evaluated,
        ai_composite_score=ds.ai_composite_score,
        score_confidence=ds.score_confidence,
        ai_framework_scores=ds.ai_framework_scores,
        expert_ratings=ds.expert_ratings,
        reviewer_notes=ds.reviewer_notes,
        review_status=ds.review_status,
        dataset_status=ds.status,
        pipeline_version=ds.metadata.pipeline_version if ds.metadata else "1.0.0",
        model_version=ds.metadata.model_version if ds.metadata else "unknown",
        created_at=ds.created_at,
        updated_at=ds.updated_at,
    )


def _to_review_response(r) -> ExpertReviewResponse:
    return ExpertReviewResponse(
        review_id=r.review_id,
        dataset_id=r.dataset_id,
        reviewer_id=r.reviewer_id,
        reviewer_name=r.reviewer_name,
        reviewer_credentials=r.reviewer_credentials,
        expert_construct_scores=r.expert_construct_scores,
        overall_score=r.overall_score,
        comments=r.comments,
        strengths=r.strengths,
        concerns=r.concerns,
        recommendations=r.recommendations,
        decision=r.decision,
        rejection_reason=r.rejection_reason,
        annotation_tags=r.annotation_tags,
        review_round=r.review_round,
        status=r.status,
        created_at=r.created_at,
        submitted_at=r.submitted_at,
    )


def _to_calibration_response(b) -> CalibrationBatchResponse:
    return CalibrationBatchResponse(
        batch_id=b.batch_id,
        batch_name=b.batch_name,
        dataset_ids=b.dataset_ids,
        reviewed_dataset_count=b.reviewed_dataset_count,
        recommended_adjustments=b.recommended_adjustments,
        policy_version_before=b.policy_version_before,
        policy_version_after=b.policy_version_after,
        adjustment_applied=b.adjustment_applied,
        total_discrepancies=b.total_discrepancies,
        constructs_with_discrepancy=b.constructs_with_discrepancy,
        mean_absolute_delta_per_construct=b.mean_absolute_delta_per_construct,
        status=b.status,
        created_at=b.created_at,
        completed_at=b.completed_at,
        metadata=b.metadata.to_dict() if b.metadata else None,
    )


def _to_export_response(e) -> ExportResponse:
    return ExportResponse(
        export_id=e.export_id,
        export_name=e.export_name,
        dataset_ids=e.dataset_ids,
        calibration_batch_id=e.calibration_batch_id,
        record_count=e.record_count,
        export_format=e.export_format,
        file_path=e.file_path,
        file_size_bytes=e.file_size_bytes,
        checksum_sha256=e.checksum_sha256,
        requested_by=e.requested_by,
        status=e.status,
        error_message=e.error_message,
        created_at=e.created_at,
        completed_at=e.completed_at,
    )
