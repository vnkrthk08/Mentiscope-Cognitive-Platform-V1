"""
Repository implementation for RAIP analytics snapshots and trends.
"""
from typing import Optional, List
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.analytics.models.dashboard_snapshot import DashboardSnapshot
from app.infrastructure.analytics.orm_models import AnalyticsSnapshotORM, AnalyticsTrendORM


class AnalyticsRepository:
    """Async repository for persisting and fetching analytics snapshots."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save_snapshot(self, snapshot: DashboardSnapshot) -> None:
        from dataclasses import asdict

        orm = AnalyticsSnapshotORM(
            snapshot_id=snapshot.snapshot_id,
            time_window=snapshot.time_window,
            assessments_json=asdict(snapshot.assessments),
            frameworks_json=asdict(snapshot.frameworks),
            evidence_json=asdict(snapshot.evidence),
            research_json=asdict(snapshot.research),
            platform_json=asdict(snapshot.platform),
            created_at=snapshot.generated_at,
        )
        self._session.add(orm)

    async def get_latest_snapshot(self, window: str = "all_time") -> Optional[AnalyticsSnapshotORM]:
        stmt = (
            select(AnalyticsSnapshotORM)
            .where(AnalyticsSnapshotORM.time_window == window)
            .order_by(desc(AnalyticsSnapshotORM.created_at))
            .limit(1)
        )
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none()
