"""
Audit, Compliance & Traceability Platform (ACTP) — API Router.

Provides 5 immutable REST endpoints for compliance auditing, end-to-end timeline reconstruction,
DAG trace graph generation, and decision reproducibility verification.

Endpoints:
  GET /audit/sessions                 List audit sessions (paginated, filterable)
  GET /audit/sessions/{id}            Get specific audit session and events
  GET /audit/timeline/{assessment_id} Generate 12-stage chronological timeline
  GET /audit/trace/{assessment_id}    Generate DAG trace graph of nodes and edges
  GET /audit/decision/{decision_id}   Get decision record with reproducible hash
"""
from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.actp.dto import (
    AuditEventResponse,
    AuditSessionListResponse,
    AuditSessionResponse,
    DecisionRecordResponse,
    TimelineResponse,
    TraceGraphResponse,
)
from app.application.actp.services.audit_collector_service import AuditCollectorService
from app.application.actp.services.timeline_generator import TimelineGenerator
from app.application.actp.services.trace_builder_service import TraceBuilderService
from app.infrastructure.actp.metrics import ACTPMetrics
from app.infrastructure.persistence.database.session import AsyncSessionLocal

router = APIRouter(prefix="/audit", tags=["Audit, Compliance & Traceability Platform"])


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


@router.get(
    "/sessions",
    response_model=AuditSessionListResponse,
    summary="List Audit Sessions",
    description="Returns paginated list of audit sessions with optional candidate filter.",
)
async def list_audit_sessions(
    candidate_id: Optional[str] = Query(None, description="Filter by candidate ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
):
    collector = AuditCollectorService(session)
    offset = (page - 1) * page_size
    sessions = await collector.list_sessions(candidate_id=candidate_id, limit=page_size, offset=offset)
    total = await collector.count_sessions(candidate_id=candidate_id)

    return AuditSessionListResponse(
        sessions=[_to_session_response(s) for s in sessions],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/sessions/{session_id}",
    response_model=AuditSessionResponse,
    summary="Get Audit Session Details",
    description="Retrieves a specific audit session by ID including all registered audit events.",
)
async def get_audit_session(
    session_id: str,
    session: AsyncSession = Depends(get_session),
):
    from app.infrastructure.actp.repositories import AuditSessionRepository

    repo = AuditSessionRepository(session)
    metrics = ACTPMetrics(session)

    audit_session = await repo.get_by_id(session_id)
    if not audit_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit session '{session_id}' not found.",
        )

    await metrics.record_audit_session_accessed(session_id, len(audit_session.events))
    await session.commit()
    return _to_session_response(audit_session)


@router.get(
    "/timeline/{assessment_id}",
    response_model=TimelineResponse,
    summary="Generate Assessment Timeline",
    description="Reconstructs chronological 12-stage execution timeline for an assessment from initial session creation to model governance comparison.",
)
async def get_assessment_timeline(
    assessment_id: str,
    session: AsyncSession = Depends(get_session),
):
    tg = TimelineGenerator(session)
    metrics = ACTPMetrics(session)

    try:
        timeline_data = await tg.generate_timeline(assessment_id)
        await metrics.record_timeline_generated(assessment_id, timeline_data["total_steps"])
        await session.commit()
        return timeline_data
    except ValueError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.get(
    "/trace/{assessment_id}",
    response_model=TraceGraphResponse,
    summary="Generate DAG Trace Graph",
    description="Generates Directed Acyclic Graph (DAG) of nodes and edges connecting models, evidence, evaluations, scores, and research actions.",
)
async def get_assessment_trace(
    assessment_id: str,
    session: AsyncSession = Depends(get_session),
):
    tb = TraceBuilderService(session)
    metrics = ACTPMetrics(session)

    try:
        trace_data = await tb.generate_trace(assessment_id)
        await metrics.record_trace_generated(
            assessment_id, trace_data["node_count"], trace_data["edge_count"]
        )
        await session.commit()
        return trace_data
    except ValueError as exc:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )


@router.get(
    "/decision/{decision_id}",
    response_model=DecisionRecordResponse,
    summary="Get Decision Record",
    description="Retrieves a specific decision record containing full score explanations, evidence references, invocation provenance, and SHA-256 reproducible hash.",
)
async def get_decision_record(
    decision_id: str,
    session: AsyncSession = Depends(get_session),
):
    collector = AuditCollectorService(session)

    # Ensure pipeline reconstructed if needed
    decision = await collector.get_decision_by_id(decision_id)
    if not decision:
        # Try fetching session from prefix if decision_id matches dec-{assessment_id[:8]}
        assessment_prefix = decision_id.replace("dec-", "")
        await collector.get_or_reconstruct_session(assessment_prefix)
        await session.commit()
        decision = await collector.get_decision_by_id(decision_id)

    if not decision:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Decision record '{decision_id}' not found.",
        )

    return _to_decision_response(decision)


# ---------------------------------------------------------------------------
# Converters
# ---------------------------------------------------------------------------


def _to_session_response(s) -> AuditSessionResponse:
    return AuditSessionResponse(
        session_id=s.session_id,
        assessment_id=s.assessment_id,
        candidate_id=s.candidate_id,
        scenario_id=s.scenario_id,
        session_status=s.session_status,
        total_events=len(s.events),
        metadata=s.metadata.to_dict() if s.metadata else None,
        events=[_to_event_response(e) for e in s.events],
        started_at=s.started_at.isoformat() if s.started_at else "",
        completed_at=s.completed_at.isoformat() if s.completed_at else None,
    )


def _to_event_response(e) -> AuditEventResponse:
    return AuditEventResponse(
        event_id=e.event_id,
        session_id=e.session_id,
        assessment_id=e.assessment_id,
        event_type=e.event_type,
        step_order=e.step_order,
        stage_name=e.stage_name,
        payload=e.payload,
        invocation=e.invocation.to_dict() if e.invocation else None,
        metadata=e.metadata.to_dict() if e.metadata else None,
        timestamp=e.timestamp.isoformat() if e.timestamp else "",
    )


def _to_decision_response(d) -> DecisionRecordResponse:
    return DecisionRecordResponse(
        record_id=d.record_id,
        decision_id=d.decision_id,
        assessment_id=d.assessment_id,
        decision_type=d.decision_type,
        input_data=d.input_data,
        output_decision=d.output_decision,
        score_explanations=[se.to_dict() for se in d.score_explanations],
        evidence_references=[er.to_dict() for er in d.evidence_references],
        pipeline_invocation=d.pipeline_invocation.to_dict() if d.pipeline_invocation else None,
        reproducible_hash=d.reproducible_hash,
        recorded_at=d.recorded_at.isoformat() if d.recorded_at else "",
    )
