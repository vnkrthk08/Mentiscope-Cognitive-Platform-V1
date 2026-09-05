"""
PVCSF Infrastructure Metrics.

Tracks operational metrics for the Psychometric Validation &
Calibration Support Framework:
  - Dataset generation timing
  - Export counts by format
  - Calibration batch statistics
  - Expert review completion rates
"""
from __future__ import annotations

import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncGenerator, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.infrastructure.research.orm_models import PVCSFMetricORM


class PVCSFMetrics:
    """
    Metrics recorder for PVCSF operations.

    All metrics are persisted to pvcsf_metrics table for
    aggregation by the research dashboard API.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record_dataset_generated(
        self,
        dataset_id: str,
        elapsed_ms: float,
        candidate_id: str,
        status: str,
    ) -> None:
        """Record timing and status for a dataset generation run."""
        orm = PVCSFMetricORM(
            id=uuid.uuid4(),
            metric_type="DATASET_GENERATED",
            entity_id=dataset_id,
            value_json={
                "elapsed_ms": round(elapsed_ms, 2),
                "candidate_id": candidate_id,
                "status": status,
                "recorded_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        self._session.add(orm)
        await self._session.flush()
        logger.debug(
            "[PVCSF Metrics] Dataset generated",
            dataset_id=dataset_id,
            elapsed_ms=elapsed_ms,
        )

    async def record_export_completed(
        self,
        export_id: str,
        export_format: str,
        record_count: int,
        file_size_bytes: int,
    ) -> None:
        """Record a completed export job."""
        orm = PVCSFMetricORM(
            id=uuid.uuid4(),
            metric_type="EXPORT_COMPLETED",
            entity_id=export_id,
            value_json={
                "export_format": export_format,
                "record_count": record_count,
                "file_size_bytes": file_size_bytes,
                "recorded_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        self._session.add(orm)
        await self._session.flush()

    async def record_expert_review(
        self,
        review_id: str,
        dataset_id: str,
        decision: str,
        review_round: int,
    ) -> None:
        """Record expert review submission."""
        orm = PVCSFMetricORM(
            id=uuid.uuid4(),
            metric_type="EXPERT_REVIEW_SUBMITTED",
            entity_id=review_id,
            value_json={
                "dataset_id": dataset_id,
                "decision": decision,
                "review_round": review_round,
                "recorded_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        self._session.add(orm)
        await self._session.flush()

    async def record_calibration_batch(
        self,
        batch_id: str,
        status: str,
        total_discrepancies: int,
        reviewed_count: int,
    ) -> None:
        """Record calibration batch lifecycle event."""
        orm = PVCSFMetricORM(
            id=uuid.uuid4(),
            metric_type="CALIBRATION_BATCH_EVENT",
            entity_id=batch_id,
            value_json={
                "status": status,
                "total_discrepancies": total_discrepancies,
                "reviewed_count": reviewed_count,
                "recorded_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        self._session.add(orm)
        await self._session.flush()
