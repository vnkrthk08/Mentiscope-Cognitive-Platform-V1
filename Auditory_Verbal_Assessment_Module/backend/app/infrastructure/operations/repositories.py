"""
Async SQLAlchemy Repositories for POSRP (Platform Operations & Site Reliability Platform).
"""
from __future__ import annotations

import uuid
from typing import List, Optional
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.operations.entities.configuration_profile import ConfigurationProfile
from app.domain.operations.entities.backup_job import BackupJob
from app.domain.operations.entities.restore_job import RestoreJob
from app.domain.operations.entities.alert_rule import AlertRule
from app.domain.operations.entities.alert_event import AlertEvent
from app.domain.operations.entities.maintenance_window import MaintenanceWindow
from app.infrastructure.operations.orm_models import (
    ConfigurationProfileORM,
    BackupJobORM,
    RestoreJobORM,
    AlertRuleORM,
    AlertEventORM,
    MaintenanceWindowORM,
)


class ConfigurationProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, profile: ConfigurationProfile) -> None:
        p_uuid = uuid.UUID(profile.profile_id)
        stmt = select(ConfigurationProfileORM).where(ConfigurationProfileORM.id == p_uuid)
        res = await self._session.execute(stmt)
        orm = res.scalar_one_or_none()

        if not orm:
            orm = ConfigurationProfileORM(
                id=p_uuid,
                profile_name=profile.profile_name,
                created_by=profile.created_by,
                config_json=profile.config_data,
                version=profile.version,
                is_active=profile.is_active,
                config_hash=profile.config_hash,
                description=profile.description,
                created_at=profile.created_at,
            )
            self._session.add(orm)
        else:
            orm.is_active = profile.is_active
            orm.config_json = profile.config_data

    async def get_active_profile(self, profile_name: str) -> Optional[ConfigurationProfile]:
        stmt = (
            select(ConfigurationProfileORM)
            .where(
                ConfigurationProfileORM.profile_name == profile_name,
                ConfigurationProfileORM.is_active == True,
            )
            .order_by(desc(ConfigurationProfileORM.version))
            .limit(1)
        )
        res = await self._session.execute(stmt)
        orm = res.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def list_profiles(self, profile_name: Optional[str] = None) -> List[ConfigurationProfile]:
        stmt = select(ConfigurationProfileORM)
        if profile_name:
            stmt = stmt.where(ConfigurationProfileORM.profile_name == profile_name)
        stmt = stmt.order_by(desc(ConfigurationProfileORM.created_at))
        res = await self._session.execute(stmt)
        return [self._to_domain(o) for o in res.scalars().all()]

    def _to_domain(self, orm: ConfigurationProfileORM) -> ConfigurationProfile:
        cp = ConfigurationProfile(
            profile_name=orm.profile_name,
            created_by=orm.created_by,
            config_data=orm.config_json or {},
            version=orm.version,
            is_active=orm.is_active,
            profile_id=str(orm.id),
            created_at=orm.created_at,
            description=orm.description or "",
        )
        cp.config_hash = orm.config_hash
        return cp


class BackupJobRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, job: BackupJob) -> None:
        j_uuid = uuid.UUID(job.job_id)
        stmt = select(BackupJobORM).where(BackupJobORM.id == j_uuid)
        res = await self._session.execute(stmt)
        orm = res.scalar_one_or_none()

        if not orm:
            orm = BackupJobORM(
                id=j_uuid,
                backup_type=job.backup_type,
                initiated_by=job.initiated_by,
                status=job.status,
                target_path=job.target_path,
                size_bytes=job.size_bytes,
                checksum=job.checksum,
                error_message=job.error_message,
                started_at=job.started_at,
                completed_at=job.completed_at,
            )
            self._session.add(orm)
        else:
            orm.status = job.status
            orm.target_path = job.target_path
            orm.size_bytes = job.size_bytes
            orm.checksum = job.checksum
            orm.error_message = job.error_message
            orm.completed_at = job.completed_at

    async def get_by_id(self, job_id: str) -> Optional[BackupJob]:
        try:
            j_uuid = uuid.UUID(job_id)
        except ValueError:
            return None

        stmt = select(BackupJobORM).where(BackupJobORM.id == j_uuid)
        res = await self._session.execute(stmt)
        orm = res.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def list_all(self) -> List[BackupJob]:
        stmt = select(BackupJobORM).order_by(desc(BackupJobORM.started_at))
        res = await self._session.execute(stmt)
        return [self._to_domain(o) for o in res.scalars().all()]

    def _to_domain(self, orm: BackupJobORM) -> BackupJob:
        return BackupJob(
            backup_type=orm.backup_type,
            initiated_by=orm.initiated_by,
            status=orm.status,
            target_path=orm.target_path or "",
            size_bytes=orm.size_bytes,
            checksum=orm.checksum or "",
            error_message=orm.error_message or "",
            job_id=str(orm.id),
            started_at=orm.started_at,
            completed_at=orm.completed_at,
        )


class RestoreJobRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, job: RestoreJob) -> None:
        j_uuid = uuid.UUID(job.job_id)
        stmt = select(RestoreJobORM).where(RestoreJobORM.id == j_uuid)
        res = await self._session.execute(stmt)
        orm = res.scalar_one_or_none()

        if not orm:
            orm = RestoreJobORM(
                id=j_uuid,
                backup_job_id=job.backup_job_id,
                restore_type=job.restore_type,
                initiated_by=job.initiated_by,
                status=job.status,
                simulation_result=job.simulation_result,
                error_message=job.error_message,
                started_at=job.started_at,
                completed_at=job.completed_at,
            )
            self._session.add(orm)
        else:
            orm.status = job.status
            orm.simulation_result = job.simulation_result
            orm.error_message = job.error_message
            orm.completed_at = job.completed_at

    async def get_by_id(self, job_id: str) -> Optional[RestoreJob]:
        try:
            j_uuid = uuid.UUID(job_id)
        except ValueError:
            return None

        stmt = select(RestoreJobORM).where(RestoreJobORM.id == j_uuid)
        res = await self._session.execute(stmt)
        orm = res.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    def _to_domain(self, orm: RestoreJobORM) -> RestoreJob:
        return RestoreJob(
            backup_job_id=orm.backup_job_id,
            restore_type=orm.restore_type,
            initiated_by=orm.initiated_by,
            status=orm.status,
            simulation_result=orm.simulation_result or "",
            error_message=orm.error_message or "",
            job_id=str(orm.id),
            started_at=orm.started_at,
            completed_at=orm.completed_at,
        )


class AlertRuleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, rule: AlertRule) -> None:
        r_uuid = uuid.UUID(rule.rule_id)
        stmt = select(AlertRuleORM).where(AlertRuleORM.id == r_uuid)
        res = await self._session.execute(stmt)
        orm = res.scalar_one_or_none()

        if not orm:
            orm = AlertRuleORM(
                id=r_uuid,
                rule_name=rule.rule_name,
                metric_name=rule.metric_name,
                condition=rule.condition,
                threshold=rule.threshold,
                severity=rule.severity,
                is_enabled=rule.is_enabled,
                cooldown_seconds=rule.cooldown_seconds,
                created_at=rule.created_at,
            )
            self._session.add(orm)

    async def list_rules(self) -> List[AlertRule]:
        stmt = select(AlertRuleORM).order_by(AlertRuleORM.rule_name)
        res = await self._session.execute(stmt)
        return [self._to_domain(o) for o in res.scalars().all()]

    async def list_rules_by_metric(self, metric_name: str) -> List[AlertRule]:
        stmt = select(AlertRuleORM).where(
            AlertRuleORM.metric_name == metric_name,
            AlertRuleORM.is_enabled == True,
        )
        res = await self._session.execute(stmt)
        return [self._to_domain(o) for o in res.scalars().all()]

    def _to_domain(self, orm: AlertRuleORM) -> AlertRule:
        return AlertRule(
            rule_name=orm.rule_name,
            metric_name=orm.metric_name,
            condition=orm.condition,
            threshold=orm.threshold,
            severity=orm.severity,
            is_enabled=orm.is_enabled,
            cooldown_seconds=orm.cooldown_seconds,
            rule_id=str(orm.id),
            created_at=orm.created_at,
        )


class AlertEventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, event: AlertEvent) -> None:
        e_uuid = uuid.UUID(event.event_id)
        stmt = select(AlertEventORM).where(AlertEventORM.id == e_uuid)
        res = await self._session.execute(stmt)
        orm = res.scalar_one_or_none()

        if not orm:
            orm = AlertEventORM(
                id=e_uuid,
                rule_id=event.rule_id,
                rule_name=event.rule_name,
                metric_name=event.metric_name,
                metric_value=event.metric_value,
                threshold=event.threshold,
                severity=event.severity,
                status=event.status,
                resolution_note=event.resolution_note,
                triggered_at=event.triggered_at,
                resolved_at=event.resolved_at,
            )
            self._session.add(orm)
        else:
            orm.status = event.status
            orm.resolution_note = event.resolution_note
            orm.resolved_at = event.resolved_at

    async def list_active(self) -> List[AlertEvent]:
        stmt = select(AlertEventORM).where(AlertEventORM.status.in_(["OPEN", "ACKNOWLEDGED"])).order_by(desc(AlertEventORM.triggered_at))
        res = await self._session.execute(stmt)
        return [self._to_domain(o) for o in res.scalars().all()]

    def _to_domain(self, orm: AlertEventORM) -> AlertEvent:
        return AlertEvent(
            rule_id=orm.rule_id,
            rule_name=orm.rule_name,
            metric_name=orm.metric_name,
            metric_value=orm.metric_value,
            threshold=orm.threshold,
            severity=orm.severity,
            status=orm.status,
            resolution_note=orm.resolution_note or "",
            event_id=str(orm.id),
            triggered_at=orm.triggered_at,
            resolved_at=orm.resolved_at,
        )
