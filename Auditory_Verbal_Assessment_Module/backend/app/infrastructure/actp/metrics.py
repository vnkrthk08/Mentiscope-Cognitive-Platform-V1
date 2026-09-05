"""
ACTPMetrics — Audit Operational Telemetry.
"""
from __future__ import annotations

from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.actp.orm_models import ACTPMetricORM


class ACTPMetrics:
    """Records operational telemetry for audit sessions, timeline, and trace queries."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record_audit_session_accessed(self, session_id: str, event_count: int) -> None:
        metric = ACTPMetricORM(
            metric_type="AUDIT_SESSION_ACCESSED",
            entity_id=session_id,
            value_json={"event_count": event_count},
        )
        self._session.add(metric)

    async def record_timeline_generated(self, assessment_id: str, total_steps: int) -> None:
        metric = ACTPMetricORM(
            metric_type="TIMELINE_GENERATED",
            entity_id=assessment_id,
            value_json={"total_steps": total_steps},
        )
        self._session.add(metric)

    async def record_trace_generated(self, assessment_id: str, node_count: int, edge_count: int) -> None:
        metric = ACTPMetricORM(
            metric_type="TRACE_GENERATED",
            entity_id=assessment_id,
            value_json={"node_count": node_count, "edge_count": edge_count},
        )
        self._session.add(metric)
