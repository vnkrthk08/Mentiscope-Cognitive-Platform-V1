"""ExperimentService — Experiment Lifecycle Management & Offline Execution."""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.governance.entities.experiment import Experiment
from app.domain.governance.entities.experiment_run import ExperimentRun
from app.domain.governance.value_objects.experiment_status import ExperimentStatus
from app.infrastructure.governance.repositories import (
    ExperimentRepository,
    ExperimentRunRepository,
    ConfigurationSnapshotRepository,
)


class ExperimentService:
    """Manages offline experiment creation, run execution, and completion."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._exp_repo = ExperimentRepository(session)
        self._run_repo = ExperimentRunRepository(session)
        self._snapshot_repo = ConfigurationSnapshotRepository(session)

    async def create_experiment(
        self,
        title: str,
        owner: str,
        baseline_snapshot_id: str,
        candidate_snapshot_id: str,
        description: str = "",
        dataset_sample_ids: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Experiment:
        exp = Experiment(
            title=title,
            owner=owner,
            baseline_snapshot_id=baseline_snapshot_id,
            candidate_snapshot_id=candidate_snapshot_id,
            description=description,
            dataset_sample_ids=dataset_sample_ids or ["sample_dataset_001"],
            metadata=metadata or {},
            status=ExperimentStatus.DRAFT,
        )

        await self._exp_repo.save(exp)
        return exp

    async def run_experiment(self, experiment_id: str) -> List[ExperimentRun]:
        """Executes offline baseline vs candidate evaluation runs for an experiment."""
        exp = await self._exp_repo.get_by_id(experiment_id)
        if not exp:
            raise ValueError(f"Experiment '{experiment_id}' not found.")

        exp.start()
        await self._exp_repo.save(exp)

        runs: List[ExperimentRun] = []
        datasets = exp.dataset_sample_ids or ["default_sample_01"]

        for ds_id in datasets:
            # 1. Baseline Run
            base_run = await self._execute_mock_run(
                experiment_id=exp.experiment_id,
                run_type="BASELINE",
                snapshot_id=exp.baseline_snapshot_id,
                dataset_id=ds_id,
                is_candidate=False,
            )
            await self._run_repo.save(base_run)
            runs.append(base_run)

            # 2. Candidate Run
            cand_run = await self._execute_mock_run(
                experiment_id=exp.experiment_id,
                run_type="CANDIDATE",
                snapshot_id=exp.candidate_snapshot_id,
                dataset_id=ds_id,
                is_candidate=True,
            )
            await self._run_repo.save(cand_run)
            runs.append(cand_run)

        exp.complete()
        await self._exp_repo.save(exp)
        return runs

    async def get_experiment_by_id(self, experiment_id: str) -> Optional[Experiment]:
        return await self._exp_repo.get_by_id(experiment_id)

    async def list_experiments(
        self, status: Optional[str] = None, limit: int = 100
    ) -> List[Experiment]:
        return await self._exp_repo.list_all(status=status, limit=limit)

    async def list_runs_for_experiment(self, experiment_id: str) -> List[ExperimentRun]:
        return await self._run_repo.list_by_experiment(experiment_id)

    async def _execute_mock_run(
        self,
        experiment_id: str,
        run_type: str,
        snapshot_id: str,
        dataset_id: str,
        is_candidate: bool,
    ) -> ExperimentRun:
        start_t = time.monotonic()
        # Simulated run outputs based on snapshot
        if is_candidate:
            transcript = f"Candidate transcript for dataset {dataset_id}. Clear articulation."
            evidence = {"CHC_Gf": 0.92, "RIASEC_I": 0.85, "observations_count": 5}
            constructs = {"fluid_reasoning": 78.0, "working_memory": 72.0}
            scores = {"CHC": 75.0, "RIASEC": 70.0, "COMPOSITE": 72.5}
            confidences = {"CHC": 0.90, "RIASEC": 0.88, "COMPOSITE": 0.89}
            latency = 1250.0
            tokens = {"prompt_tokens": 1200, "completion_tokens": 450, "total_tokens": 1650}
            cost = 0.0033
        else:
            transcript = f"Baseline transcript for dataset {dataset_id}. Standard response."
            evidence = {"CHC_Gf": 0.88, "RIASEC_I": 0.80, "observations_count": 4}
            constructs = {"fluid_reasoning": 75.0, "working_memory": 70.0}
            scores = {"CHC": 72.5, "RIASEC": 68.0, "COMPOSITE": 70.25}
            confidences = {"CHC": 0.87, "RIASEC": 0.85, "COMPOSITE": 0.86}
            latency = 1450.0
            tokens = {"prompt_tokens": 1100, "completion_tokens": 400, "total_tokens": 1500}
            cost = 0.0030

        return ExperimentRun(
            experiment_id=experiment_id,
            run_type=run_type,
            snapshot_id=snapshot_id,
            dataset_id=dataset_id,
            transcript_output=transcript,
            behavior_evidence_output=evidence,
            construct_evaluation_output=constructs,
            assessment_scores_output=scores,
            confidence_values=confidences,
            processing_latency_ms=latency,
            token_usage=tokens,
            estimated_cost_usd=cost,
            status="COMPLETED",
        )
