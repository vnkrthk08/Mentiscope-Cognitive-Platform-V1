"""
Async SQLAlchemy Repositories for MGEP (Model Governance & Experimentation Platform).
"""
from __future__ import annotations

import uuid
from typing import List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.governance.entities.model_registry import RegisteredModel
from app.domain.governance.entities.configuration_snapshot import ConfigurationSnapshot
from app.domain.governance.entities.experiment import Experiment
from app.domain.governance.entities.experiment_run import ExperimentRun
from app.domain.governance.entities.comparison_report import ComparisonReport
from app.domain.governance.value_objects.model_version import ModelVersion
from app.domain.governance.value_objects.configuration_hash import ConfigurationHash
from app.domain.governance.value_objects.experiment_status import ExperimentStatus
from app.infrastructure.governance.orm_models import (
    ModelRegistryORM,
    ConfigurationSnapshotORM,
    ExperimentORM,
    ExperimentRunORM,
    ComparisonReportORM,
)


class ModelRegistryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, model: RegisteredModel) -> None:
        model_uuid = uuid.UUID(model.model_id)
        stmt = select(ModelRegistryORM).where(ModelRegistryORM.id == model_uuid)
        res = await self._session.execute(stmt)
        orm = res.scalar_one_or_none()

        if not orm:
            orm = ModelRegistryORM(
                id=model_uuid,
                name=model.name,
                category=model.category,
                version=str(model.version),
                status=model.status,
                description=model.description,
                owner=model.owner,
                checksum=model.checksum,
                configuration_json=model.configuration,
                created_at=model.created_at,
                updated_at=model.updated_at,
            )
            self._session.add(orm)
        else:
            orm.name = model.name
            orm.category = model.category
            orm.version = str(model.version)
            orm.status = model.status
            orm.description = model.description
            orm.owner = model.owner
            orm.checksum = model.checksum
            orm.configuration_json = model.configuration
            orm.updated_at = model.updated_at

    async def get_by_id(self, model_id: str) -> Optional[RegisteredModel]:
        try:
            m_uuid = uuid.UUID(model_id)
        except ValueError:
            return None

        stmt = select(ModelRegistryORM).where(ModelRegistryORM.id == m_uuid)
        res = await self._session.execute(stmt)
        orm = res.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def list_all(
        self, category: Optional[str] = None, status: Optional[str] = None, limit: int = 100
    ) -> List[RegisteredModel]:
        stmt = select(ModelRegistryORM).where(ModelRegistryORM.is_deleted == False)
        if category:
            stmt = stmt.where(ModelRegistryORM.category == category.upper())
        if status:
            stmt = stmt.where(ModelRegistryORM.status == status.upper())
        stmt = stmt.order_by(desc(ModelRegistryORM.created_at)).limit(limit)

        res = await self._session.execute(stmt)
        return [self._to_domain(o) for o in res.scalars().all()]

    def _to_domain(self, orm: ModelRegistryORM) -> RegisteredModel:
        return RegisteredModel(
            model_id=str(orm.id),
            name=orm.name,
            category=orm.category,
            version=ModelVersion(orm.version),
            owner=orm.owner,
            description=orm.description or "",
            checksum=orm.checksum,
            configuration=orm.configuration_json or {},
            status=orm.status,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )


class ConfigurationSnapshotRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, snapshot: ConfigurationSnapshot) -> None:
        snap_uuid = uuid.UUID(snapshot.snapshot_id)
        stmt = select(ConfigurationSnapshotORM).where(ConfigurationSnapshotORM.id == snap_uuid)
        res = await self._session.execute(stmt)
        orm = res.scalar_one_or_none()

        if not orm:
            orm = ConfigurationSnapshotORM(
                id=snap_uuid,
                snapshot_name=snapshot.snapshot_name,
                config_hash=str(snapshot.config_hash) if snapshot.config_hash else "",
                speech_model_id=snapshot.speech_model_id,
                prompt_template_id=snapshot.prompt_template_id,
                llm_model_id=snapshot.llm_model_id,
                behavior_extractor_id=snapshot.behavior_extractor_id,
                construct_policy_id=snapshot.construct_policy_id,
                scoring_policy_id=snapshot.scoring_policy_id,
                full_config_json=snapshot.full_config,
                created_by=snapshot.created_by,
                created_at=snapshot.created_at,
            )
            self._session.add(orm)

    async def get_by_id(self, snapshot_id: str) -> Optional[ConfigurationSnapshot]:
        try:
            s_uuid = uuid.UUID(snapshot_id)
        except ValueError:
            return None

        stmt = select(ConfigurationSnapshotORM).where(ConfigurationSnapshotORM.id == s_uuid)
        res = await self._session.execute(stmt)
        orm = res.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    def _to_domain(self, orm: ConfigurationSnapshotORM) -> ConfigurationSnapshot:
        return ConfigurationSnapshot(
            snapshot_id=str(orm.id),
            snapshot_name=orm.snapshot_name,
            config_hash=ConfigurationHash(orm.config_hash) if orm.config_hash else None,
            speech_model_id=orm.speech_model_id,
            prompt_template_id=orm.prompt_template_id,
            llm_model_id=orm.llm_model_id,
            behavior_extractor_id=orm.behavior_extractor_id,
            construct_policy_id=orm.construct_policy_id,
            scoring_policy_id=orm.scoring_policy_id,
            full_config=orm.full_config_json or {},
            created_by=orm.created_by,
            created_at=orm.created_at,
        )


class ExperimentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, experiment: Experiment) -> None:
        exp_uuid = uuid.UUID(experiment.experiment_id)
        stmt = select(ExperimentORM).where(ExperimentORM.id == exp_uuid)
        res = await self._session.execute(stmt)
        orm = res.scalar_one_or_none()

        status_str = (
            experiment.status.value
            if isinstance(experiment.status, ExperimentStatus)
            else str(experiment.status)
        )

        if not orm:
            orm = ExperimentORM(
                id=exp_uuid,
                title=experiment.title,
                description=experiment.description,
                owner=experiment.owner,
                status=status_str,
                baseline_snapshot_id=experiment.baseline_snapshot_id,
                candidate_snapshot_id=experiment.candidate_snapshot_id,
                dataset_sample_ids=experiment.dataset_sample_ids,
                metadata_json=experiment.metadata,
                created_at=experiment.created_at,
                completed_at=experiment.completed_at,
            )
            self._session.add(orm)
        else:
            orm.title = experiment.title
            orm.description = experiment.description
            orm.status = status_str
            orm.dataset_sample_ids = experiment.dataset_sample_ids
            orm.metadata_json = experiment.metadata
            orm.completed_at = experiment.completed_at

    async def get_by_id(self, experiment_id: str) -> Optional[Experiment]:
        try:
            e_uuid = uuid.UUID(experiment_id)
        except ValueError:
            return None

        stmt = select(ExperimentORM).where(ExperimentORM.id == e_uuid)
        res = await self._session.execute(stmt)
        orm = res.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def list_all(
        self, status: Optional[str] = None, limit: int = 100
    ) -> List[Experiment]:
        stmt = select(ExperimentORM).where(ExperimentORM.is_deleted == False)
        if status:
            stmt = stmt.where(ExperimentORM.status == status.upper())
        stmt = stmt.order_by(desc(ExperimentORM.created_at)).limit(limit)

        res = await self._session.execute(stmt)
        return [self._to_domain(o) for o in res.scalars().all()]

    def _to_domain(self, orm: ExperimentORM) -> Experiment:
        return Experiment(
            experiment_id=str(orm.id),
            title=orm.title,
            description=orm.description or "",
            owner=orm.owner,
            status=ExperimentStatus(orm.status),
            baseline_snapshot_id=orm.baseline_snapshot_id,
            candidate_snapshot_id=orm.candidate_snapshot_id,
            dataset_sample_ids=orm.dataset_sample_ids or [],
            metadata=orm.metadata_json or {},
            created_at=orm.created_at,
            completed_at=orm.completed_at,
        )


class ExperimentRunRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, run: ExperimentRun) -> None:
        run_uuid = uuid.UUID(run.run_id)
        exp_uuid = uuid.UUID(run.experiment_id)

        stmt = select(ExperimentRunORM).where(ExperimentRunORM.id == run_uuid)
        res = await self._session.execute(stmt)
        orm = res.scalar_one_or_none()

        if not orm:
            orm = ExperimentRunORM(
                id=run_uuid,
                experiment_id=exp_uuid,
                run_type=run.run_type,
                snapshot_id=run.snapshot_id,
                dataset_id=run.dataset_id,
                transcript_output=run.transcript_output,
                behavior_evidence_output=run.behavior_evidence_output,
                construct_evaluation_output=run.construct_evaluation_output,
                assessment_scores_output=run.assessment_scores_output,
                confidence_values=run.confidence_values,
                processing_latency_ms=run.processing_latency_ms,
                token_usage_json=run.token_usage,
                estimated_cost_usd=run.estimated_cost_usd,
                status=run.status,
                executed_at=run.executed_at,
            )
            self._session.add(orm)

    async def list_by_experiment(self, experiment_id: str) -> List[ExperimentRun]:
        try:
            exp_uuid = uuid.UUID(experiment_id)
        except ValueError:
            return []

        stmt = select(ExperimentRunORM).where(ExperimentRunORM.experiment_id == exp_uuid)
        res = await self._session.execute(stmt)
        return [self._to_domain(o) for o in res.scalars().all()]

    def _to_domain(self, orm: ExperimentRunORM) -> ExperimentRun:
        return ExperimentRun(
            run_id=str(orm.id),
            experiment_id=str(orm.experiment_id),
            run_type=orm.run_type,
            snapshot_id=orm.snapshot_id,
            dataset_id=orm.dataset_id,
            transcript_output=orm.transcript_output or "",
            behavior_evidence_output=orm.behavior_evidence_output or {},
            construct_evaluation_output=orm.construct_evaluation_output or {},
            assessment_scores_output=orm.assessment_scores_output or {},
            confidence_values=orm.confidence_values or {},
            processing_latency_ms=orm.processing_latency_ms,
            token_usage=orm.token_usage_json or {},
            estimated_cost_usd=orm.estimated_cost_usd,
            status=orm.status,
            executed_at=orm.executed_at,
        )


class ComparisonReportRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, report: ComparisonReport) -> None:
        rep_uuid = uuid.UUID(report.report_id)
        exp_uuid = uuid.UUID(report.experiment_id)

        stmt = select(ComparisonReportORM).where(ComparisonReportORM.id == rep_uuid)
        res = await self._session.execute(stmt)
        orm = res.scalar_one_or_none()

        if not orm:
            orm = ComparisonReportORM(
                id=rep_uuid,
                experiment_id=exp_uuid,
                baseline_run_id=uuid.UUID(report.baseline_run_id),
                candidate_run_id=uuid.UUID(report.candidate_run_id),
                prompt_diff_summary=report.prompt_diff_summary,
                evidence_diff_summary=report.evidence_diff_summary,
                evaluation_diff_summary=report.evaluation_diff_summary,
                score_deltas=report.score_deltas,
                latency_delta_ms=report.latency_delta_ms,
                cost_delta_usd=report.cost_delta_usd,
                overall_recommendation=report.overall_recommendation,
                generated_at=report.generated_at,
            )
            self._session.add(orm)

    async def get_by_experiment(self, experiment_id: str) -> Optional[ComparisonReport]:
        try:
            exp_uuid = uuid.UUID(experiment_id)
        except ValueError:
            return None

        stmt = (
            select(ComparisonReportORM)
            .where(ComparisonReportORM.experiment_id == exp_uuid)
            .order_by(desc(ComparisonReportORM.generated_at))
            .limit(1)
        )
        res = await self._session.execute(stmt)
        orm = res.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    def _to_domain(self, orm: ComparisonReportORM) -> ComparisonReport:
        return ComparisonReport(
            report_id=str(orm.id),
            experiment_id=str(orm.experiment_id),
            baseline_run_id=str(orm.baseline_run_id),
            candidate_run_id=str(orm.candidate_run_id),
            prompt_diff_summary=orm.prompt_diff_summary or {},
            evidence_diff_summary=orm.evidence_diff_summary or {},
            evaluation_diff_summary=orm.evaluation_diff_summary or {},
            score_deltas=orm.score_deltas or {},
            latency_delta_ms=orm.latency_delta_ms,
            cost_delta_usd=orm.cost_delta_usd,
            overall_recommendation=orm.overall_recommendation,
            generated_at=orm.generated_at,
        )
