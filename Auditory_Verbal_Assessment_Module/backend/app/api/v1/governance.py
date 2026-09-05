"""
Model Governance & Experimentation Platform (MGEP) — API Router.

Provides REST endpoints to register, version, snapshot, execute, compare, and audit
AI pipeline components and experiments.

Endpoints:
  POST /governance/models          Register a new AI component or model entry
  GET  /governance/models          List all registered models (filterable)
  POST /governance/snapshots       Create a configuration snapshot
  POST /governance/experiments     Create an offline experiment
  GET  /governance/experiments     List all experiments
  GET  /governance/experiments/{id} Get experiment details including runs
  POST /governance/experiments/{id}/run Execute experiment runs
  POST /governance/compare         Compare baseline vs candidate runs and generate report
"""
from __future__ import annotations

import time
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.governance.dto import (
    CompareRunsRequest,
    ComparisonReportResponse,
    CreateExperimentRequest,
    CreateSnapshotRequest,
    ConfigurationSnapshotResponse,
    ExperimentResponse,
    ExperimentRunResponse,
    RegisterModelRequest,
    RegisteredModelResponse,
)
from app.application.governance.services.comparison_service import ComparisonService
from app.application.governance.services.experiment_service import ExperimentService
from app.application.governance.services.registry_service import RegistryService
from app.infrastructure.governance.metrics import MGEPMetrics
from app.infrastructure.persistence.database.session import AsyncSessionLocal

router = APIRouter(prefix="/governance", tags=["Model Governance & Experimentation Platform"])


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


# ---------------------------------------------------------------------------
# 1. Model Registry Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/models",
    response_model=RegisteredModelResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register Model Component",
    description="Registers a new AI component entry (Speech Model, Prompt Template, LLM Model, Behavior Extractor, Construct Policy, Scoring Policy) with automated SHA-256 checksumming.",
)
async def register_model(
    req: RegisterModelRequest,
    session: AsyncSession = Depends(get_session),
):
    svc = RegistryService(session)
    metrics = MGEPMetrics(session)

    try:
        model = await svc.register_model(
            name=req.name,
            category=req.category,
            version_str=req.version,
            owner=req.owner,
            description=req.description,
            configuration=req.configuration,
        )
        await metrics.record_model_registered(model.model_id, model.category, model.name)
        await session.commit()
        return _to_model_response(model)
    except Exception as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model registration failed: {str(exc)}",
        )


@router.get(
    "/models",
    response_model=List[RegisteredModelResponse],
    summary="List Registered Models",
    description="Returns registered models and components, filterable by category and status.",
)
async def list_models(
    category: Optional[str] = Query(None, description="Category filter (SPEECH, LLM_MODEL, PROMPT_TEMPLATE, etc.)"),
    status_filter: Optional[str] = Query(None, alias="status", description="Status filter (ACTIVE, DEPRECATED, ARCHIVED)"),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
):
    svc = RegistryService(session)
    models = await svc.list_models(category=category, status=status_filter, limit=limit)
    return [_to_model_response(m) for m in models]


# ---------------------------------------------------------------------------
# 2. Configuration Snapshot Endpoint
# ---------------------------------------------------------------------------


@router.post(
    "/snapshots",
    response_model=ConfigurationSnapshotResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Configuration Snapshot",
    description="Creates an immutable snapshot of a full pipeline component configuration tagged with SHA-256 hash integrity.",
)
async def create_snapshot(
    req: CreateSnapshotRequest,
    session: AsyncSession = Depends(get_session),
):
    svc = RegistryService(session)

    try:
        snapshot = await svc.create_snapshot(
            snapshot_name=req.snapshot_name,
            created_by=req.created_by,
            speech_model_id=req.speech_model_id,
            prompt_template_id=req.prompt_template_id,
            llm_model_id=req.llm_model_id,
            behavior_extractor_id=req.behavior_extractor_id,
            construct_policy_id=req.construct_policy_id,
            scoring_policy_id=req.scoring_policy_id,
            full_config=req.full_config,
        )
        await session.commit()
        return _to_snapshot_response(snapshot)
    except Exception as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Snapshot creation failed: {str(exc)}",
        )


# ---------------------------------------------------------------------------
# 3. Experiment Endpoints
# ---------------------------------------------------------------------------


@router.post(
    "/experiments",
    response_model=ExperimentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Experiment",
    description="Creates a new offline experiment container comparing a baseline snapshot against a candidate snapshot.",
)
async def create_experiment(
    req: CreateExperimentRequest,
    session: AsyncSession = Depends(get_session),
):
    exp_svc = ExperimentService(session)
    metrics = MGEPMetrics(session)

    try:
        exp = await exp_svc.create_experiment(
            title=req.title,
            owner=req.owner,
            baseline_snapshot_id=req.baseline_snapshot_id,
            candidate_snapshot_id=req.candidate_snapshot_id,
            description=req.description,
            dataset_sample_ids=req.dataset_sample_ids,
            metadata=req.metadata,
        )
        await metrics.record_experiment_created(exp.experiment_id, exp.owner)
        await session.commit()
        return _to_experiment_response(exp, [])
    except Exception as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Experiment creation failed: {str(exc)}",
        )


@router.get(
    "/experiments",
    response_model=List[ExperimentResponse],
    summary="List Experiments",
    description="Returns all experiments with optional status filtering.",
)
async def list_experiments(
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
):
    exp_svc = ExperimentService(session)
    experiments = await exp_svc.list_experiments(status=status_filter, limit=limit)
    res = []
    for exp in experiments:
        runs = await exp_svc.list_runs_for_experiment(exp.experiment_id)
        res.append(_to_experiment_response(exp, runs))
    return res


@router.get(
    "/experiments/{experiment_id}",
    response_model=ExperimentResponse,
    summary="Get Experiment Details",
    description="Retrieves a specific experiment by ID including all associated execution runs.",
)
async def get_experiment(
    experiment_id: str,
    session: AsyncSession = Depends(get_session),
):
    exp_svc = ExperimentService(session)
    exp = await exp_svc.get_experiment_by_id(experiment_id)
    if not exp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Experiment '{experiment_id}' not found.",
        )
    runs = await exp_svc.list_runs_for_experiment(experiment_id)
    return _to_experiment_response(exp, runs)


@router.post(
    "/experiments/{experiment_id}/run",
    response_model=List[ExperimentRunResponse],
    summary="Execute Experiment Runs",
    description="Triggers offline execution for baseline and candidate snapshots on assigned sample datasets.",
)
async def run_experiment(
    experiment_id: str,
    session: AsyncSession = Depends(get_session),
):
    exp_svc = ExperimentService(session)
    metrics = MGEPMetrics(session)
    start_ms = time.monotonic() * 1000

    try:
        runs = await exp_svc.run_experiment(experiment_id)
        elapsed_ms = (time.monotonic() * 1000) - start_ms
        await metrics.record_experiment_completed(experiment_id, len(runs), elapsed_ms)
        await session.commit()
        return [_to_run_response(r) for r in runs]
    except Exception as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Experiment execution failed: {str(exc)}",
        )


# ---------------------------------------------------------------------------
# 4. Comparison Endpoint
# ---------------------------------------------------------------------------


@router.post(
    "/compare",
    response_model=ComparisonReportResponse,
    status_code=status.HTTP_200_OK,
    summary="Compare Experiment Runs",
    description="Computes granular diffs across prompts, behavior evidence, construct evaluations, scores, latency, tokens, and cost.",
)
async def compare_runs(
    req: CompareRunsRequest,
    session: AsyncSession = Depends(get_session),
):
    comp_svc = ComparisonService(session)

    try:
        report = await comp_svc.compare_runs(
            experiment_id=req.experiment_id,
            baseline_run_id=req.baseline_run_id,
            candidate_run_id=req.candidate_run_id,
        )
        await session.commit()
        return _to_comparison_response(report)
    except Exception as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Comparison failed: {str(exc)}",
        )


# ---------------------------------------------------------------------------
# DTO Converters
# ---------------------------------------------------------------------------


def _to_model_response(m) -> RegisteredModelResponse:
    return RegisteredModelResponse(
        model_id=m.model_id,
        name=m.name,
        category=m.category,
        version=str(m.version),
        owner=m.owner,
        description=m.description,
        checksum=m.checksum,
        configuration=m.configuration,
        status=m.status,
        created_at=m.created_at.isoformat() if m.created_at else "",
        updated_at=m.updated_at.isoformat() if m.updated_at else "",
    )


def _to_snapshot_response(s) -> ConfigurationSnapshotResponse:
    return ConfigurationSnapshotResponse(
        snapshot_id=s.snapshot_id,
        snapshot_name=s.snapshot_name,
        config_hash=str(s.config_hash) if s.config_hash else "",
        speech_model_id=s.speech_model_id,
        prompt_template_id=s.prompt_template_id,
        llm_model_id=s.llm_model_id,
        behavior_extractor_id=s.behavior_extractor_id,
        construct_policy_id=s.construct_policy_id,
        scoring_policy_id=s.scoring_policy_id,
        full_config=s.full_config,
        created_by=s.created_by,
        created_at=s.created_at.isoformat() if s.created_at else "",
    )


def _to_run_response(r) -> ExperimentRunResponse:
    return ExperimentRunResponse(
        run_id=r.run_id,
        experiment_id=r.experiment_id,
        run_type=r.run_type,
        snapshot_id=r.snapshot_id,
        dataset_id=r.dataset_id,
        transcript_output=r.transcript_output,
        behavior_evidence_output=r.behavior_evidence_output,
        construct_evaluation_output=r.construct_evaluation_output,
        assessment_scores_output=r.assessment_scores_output,
        confidence_values=r.confidence_values,
        processing_latency_ms=r.processing_latency_ms,
        token_usage=r.token_usage,
        estimated_cost_usd=r.estimated_cost_usd,
        status=r.status,
        executed_at=r.executed_at.isoformat() if r.executed_at else "",
    )


def _to_experiment_response(exp, runs) -> ExperimentResponse:
    status_str = exp.status.value if hasattr(exp.status, "value") else str(exp.status)
    return ExperimentResponse(
        experiment_id=exp.experiment_id,
        title=exp.title,
        description=exp.description,
        owner=exp.owner,
        status=status_str,
        baseline_snapshot_id=exp.baseline_snapshot_id,
        candidate_snapshot_id=exp.candidate_snapshot_id,
        dataset_sample_ids=exp.dataset_sample_ids,
        metadata=exp.metadata,
        created_at=exp.created_at.isoformat() if exp.created_at else "",
        completed_at=exp.completed_at.isoformat() if exp.completed_at else None,
        runs=[_to_run_response(r) for r in runs],
    )


def _to_comparison_response(rep) -> ComparisonReportResponse:
    return ComparisonReportResponse(
        report_id=rep.report_id,
        experiment_id=rep.experiment_id,
        baseline_run_id=rep.baseline_run_id,
        candidate_run_id=rep.candidate_run_id,
        prompt_diff_summary=rep.prompt_diff_summary,
        evidence_diff_summary=rep.evidence_diff_summary,
        evaluation_diff_summary=rep.evaluation_diff_summary,
        score_deltas=rep.score_deltas,
        latency_delta_ms=rep.latency_delta_ms,
        cost_delta_usd=rep.cost_delta_usd,
        overall_recommendation=rep.overall_recommendation,
        generated_at=rep.generated_at.isoformat() if rep.generated_at else "",
    )
