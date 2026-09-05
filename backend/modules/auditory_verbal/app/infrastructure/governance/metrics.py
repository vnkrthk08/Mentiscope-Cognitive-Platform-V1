"""
MGEPMetrics — Governance Operational Telemetry.
"""
from __future__ import annotations

from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.governance.orm_models import MGEPMetricORM


class MGEPMetrics:
    """Records operational metrics for MGEP model registry and experiments."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record_model_registered(self, model_id: str, category: str, name: str) -> None:
        metric = MGEPMetricORM(
            metric_type="MODEL_REGISTERED",
            entity_id=model_id,
            value_json={"category": category, "name": name},
        )
        self._session.add(metric)

    async def record_experiment_created(self, experiment_id: str, owner: str) -> None:
        metric = MGEPMetricORM(
            metric_type="EXPERIMENT_CREATED",
            entity_id=experiment_id,
            value_json={"owner": owner},
        )
        self._session.add(metric)

    async def record_experiment_completed(
        self, experiment_id: str, total_runs: int, elapsed_ms: float
    ) -> None:
        metric = MGEPMetricORM(
            metric_type="EXPERIMENT_COMPLETED",
            entity_id=experiment_id,
            value_json={"total_runs": total_runs, "elapsed_ms": elapsed_ms},
        )
        self._session.add(metric)
