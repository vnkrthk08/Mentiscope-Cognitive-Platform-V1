"""
Research Analytics & Insights Platform (RAIP) — API Router.

Provides 6 GET endpoints for visual dashboards, trends, operational quality,
and research tracking.

All endpoints are read-only.
NO psychometric statistics (Cronbach Alpha, ICC, Factor Analysis, etc.) are performed.

Endpoints:
  GET /analytics/dashboard    Unified dashboard snapshot
  GET /analytics/assessments  Assessment activity, completion rate, scenario counts
  GET /analytics/frameworks   CHC, RIASEC, Personality, Emotional Regulation metrics
  GET /analytics/evidence     Behavior evidence quality, observation frequencies
  GET /analytics/research     PVCSF research datasets, expert reviews, calibration, exports
  GET /analytics/platform     STT/LLM provider usage, latencies, pipeline completion
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.analytics.dto import (
    AssessmentAnalyticsResponse,
    DashboardSnapshotResponse,
    EvidenceAnalyticsResponse,
    FrameworkAnalyticsResponse,
    PlatformAnalyticsResponse,
    ResearchAnalyticsResponse,
)
from app.application.analytics.services.analytics_aggregator import AnalyticsAggregatorService
from app.domain.analytics.value_objects.time_window import TimeWindow
from app.infrastructure.persistence.database.session import AsyncSessionLocal

router = APIRouter(prefix="/analytics", tags=["Research Analytics & Insights Platform"])


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


def _parse_time_window(window_str: Optional[str]) -> TimeWindow:
    if not window_str:
        return TimeWindow.ALL_TIME
    try:
        return TimeWindow(window_str.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid time window '{window_str}'. Allowed values: daily, weekly, monthly, all_time",
        )


@router.get(
    "/dashboard",
    response_model=DashboardSnapshotResponse,
    summary="Get Complete Analytics Dashboard",
    description="Returns aggregate metrics across all 5 analytics domains: Assessments, Frameworks, Evidence, Research, and Platform.",
)
async def get_dashboard_analytics(
    window: Optional[str] = Query(None, description="Time window: daily, weekly, monthly, all_time"),
    session: AsyncSession = Depends(get_session),
):
    tw = _parse_time_window(window)
    svc = AnalyticsAggregatorService(session)
    snapshot = await svc.aggregate_dashboard(tw)
    return snapshot


@router.get(
    "/assessments",
    response_model=AssessmentAnalyticsResponse,
    summary="Get Assessment Activity Analytics",
    description="Returns assessment completion rates, total counts, scenario breakdowns, and time-series trends.",
)
async def get_assessment_analytics(
    window: Optional[str] = Query(None, description="Time window: daily, weekly, monthly, all_time"),
    session: AsyncSession = Depends(get_session),
):
    tw = _parse_time_window(window)
    svc = AnalyticsAggregatorService(session)
    return await svc.aggregate_assessments(tw)


@router.get(
    "/frameworks",
    response_model=FrameworkAnalyticsResponse,
    summary="Get Framework Score Analytics",
    description="Returns average scores, confidence distributions, and coverage across CHC, RIASEC, Personality, and Emotional Regulation.",
)
async def get_framework_analytics(
    window: Optional[str] = Query(None, description="Time window: daily, weekly, monthly, all_time"),
    session: AsyncSession = Depends(get_session),
):
    tw = _parse_time_window(window)
    svc = AnalyticsAggregatorService(session)
    return await svc.aggregate_frameworks(tw)


@router.get(
    "/evidence",
    response_model=EvidenceAnalyticsResponse,
    summary="Get Behavioral Evidence Analytics",
    description="Returns evidence counts, quality scores, observation frequency rankings, and evidence utilization rates.",
)
async def get_evidence_analytics(
    window: Optional[str] = Query(None, description="Time window: daily, weekly, monthly, all_time"),
    session: AsyncSession = Depends(get_session),
):
    tw = _parse_time_window(window)
    svc = AnalyticsAggregatorService(session)
    return await svc.aggregate_evidence(tw)


@router.get(
    "/research",
    response_model=ResearchAnalyticsResponse,
    summary="Get Research Framework Analytics",
    description="Returns PVCSF dataset metrics, expert review workloads, calibration batch statuses, and export histories.",
)
async def get_research_analytics(
    window: Optional[str] = Query(None, description="Time window: daily, weekly, monthly, all_time"),
    session: AsyncSession = Depends(get_session),
):
    tw = _parse_time_window(window)
    svc = AnalyticsAggregatorService(session)
    return await svc.aggregate_research(tw)


@router.get(
    "/platform",
    response_model=PlatformAnalyticsResponse,
    summary="Get Platform Operational Analytics",
    description="Returns Speech/LLM provider usage distributions, processing latencies, completion rates, and error frequencies.",
)
async def get_platform_analytics(
    window: Optional[str] = Query(None, description="Time window: daily, weekly, monthly, all_time"),
    session: AsyncSession = Depends(get_session),
):
    tw = _parse_time_window(window)
    svc = AnalyticsAggregatorService(session)
    return await svc.aggregate_platform(tw)
