"""
POSRPMetrics — Operations Telemetry Logger.
"""
from __future__ import annotations

from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.operations.orm_models import POSRPMetricORM


class POSRPMetrics:
    """Records operational telemetry for health checks, backups, restores, and alerts."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record_health_check(self, overall_status: str, healthy_count: int) -> None:
        metric = POSRPMetricORM(
            metric_type="HEALTH_CHECK",
            value_json={"overall_status": overall_status, "healthy_count": healthy_count},
        )
        self._session.add(metric)

    async def record_backup_initiated(self, job_id: str, backup_type: str) -> None:
        metric = POSRPMetricORM(
            metric_type="BACKUP_INITIATED",
            value_json={"job_id": job_id, "backup_type": backup_type},
        )
        self._session.add(metric)

    async def record_restore_executed(self, job_id: str, restore_type: str, status: str) -> None:
        metric = POSRPMetricORM(
            metric_type="RESTORE_EXECUTED",
            value_json={"job_id": job_id, "restore_type": restore_type, "status": status},
        )
        self._session.add(metric)
