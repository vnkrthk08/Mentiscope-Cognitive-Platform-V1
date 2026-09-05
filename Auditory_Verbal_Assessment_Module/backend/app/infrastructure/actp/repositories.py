"""
Async SQLAlchemy Repositories for ACTP (Audit, Compliance & Traceability Platform).
"""
from __future__ import annotations

import uuid
from typing import List, Optional
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.actp.entities.audit_session import AuditSession
from app.domain.actp.entities.audit_event import AuditEvent
from app.domain.actp.entities.decision_record import DecisionRecord
from app.domain.actp.value_objects.audit_metadata import AuditMetadata
from app.domain.actp.value_objects.pipeline_invocation import PipelineInvocation
from app.domain.actp.value_objects.evidence_reference import EvidenceReference
from app.domain.actp.value_objects.score_explanation import ScoreExplanation
from app.infrastructure.actp.orm_models import (
    AuditSessionORM,
    AuditEventORM,
    DecisionRecordORM,
)


class AuditSessionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, audit_session: AuditSession) -> None:
        s_uuid = uuid.UUID(audit_session.session_id)
        stmt = select(AuditSessionORM).where(AuditSessionORM.id == s_uuid)
        res = await self._session.execute(stmt)
        orm = res.scalar_one_or_none()

        if not orm:
            orm = AuditSessionORM(
                id=s_uuid,
                assessment_id=audit_session.assessment_id,
                candidate_id=audit_session.candidate_id,
                scenario_id=audit_session.scenario_id,
                session_status=audit_session.session_status,
                total_events=len(audit_session.events),
                metadata_json=audit_session.metadata.to_dict() if audit_session.metadata else {},
                started_at=audit_session.started_at,
                completed_at=audit_session.completed_at,
            )
            self._session.add(orm)
        else:
            orm.session_status = audit_session.session_status
            orm.total_events = len(audit_session.events)
            orm.completed_at = audit_session.completed_at

    async def get_by_id(self, session_id: str) -> Optional[AuditSession]:
        try:
            s_uuid = uuid.UUID(session_id)
        except ValueError:
            return None

        stmt = select(AuditSessionORM).where(AuditSessionORM.id == s_uuid)
        res = await self._session.execute(stmt)
        orm = res.scalar_one_or_none()
        if not orm:
            return None

        events = await AuditEventRepository(self._session).list_by_session_id(str(orm.id))
        return self._to_domain(orm, events)

    async def get_by_assessment_id(self, assessment_id: str) -> Optional[AuditSession]:
        stmt = (
            select(AuditSessionORM)
            .where(AuditSessionORM.assessment_id == assessment_id)
            .order_by(desc(AuditSessionORM.started_at))
            .limit(1)
        )
        res = await self._session.execute(stmt)
        orm = res.scalar_one_or_none()
        if not orm:
            return None

        events = await AuditEventRepository(self._session).list_by_session_id(str(orm.id))
        return self._to_domain(orm, events)

    async def list_all(
        self, candidate_id: Optional[str] = None, limit: int = 50, offset: int = 0
    ) -> List[AuditSession]:
        stmt = select(AuditSessionORM)
        if candidate_id:
            stmt = stmt.where(AuditSessionORM.candidate_id == candidate_id)
        stmt = stmt.order_by(desc(AuditSessionORM.started_at)).limit(limit).offset(offset)

        res = await self._session.execute(stmt)
        orms = res.scalars().all()
        result = []
        for o in orms:
            events = await AuditEventRepository(self._session).list_by_session_id(str(o.id))
            result.append(self._to_domain(o, events))
        return result

    async def count(self, candidate_id: Optional[str] = None) -> int:
        stmt = select(func.count(AuditSessionORM.id))
        if candidate_id:
            stmt = stmt.where(AuditSessionORM.candidate_id == candidate_id)
        res = await self._session.execute(stmt)
        return res.scalar_one_or_none() or 0

    def _to_domain(self, orm: AuditSessionORM, events: List[AuditEvent]) -> AuditSession:
        return AuditSession(
            session_id=str(orm.id),
            assessment_id=orm.assessment_id,
            candidate_id=orm.candidate_id,
            scenario_id=orm.scenario_id,
            session_status=orm.session_status,
            metadata=AuditMetadata(tags=orm.metadata_json.get("tags", {})) if orm.metadata_json else None,
            events=events,
            started_at=orm.started_at,
            completed_at=orm.completed_at,
        )


class AuditEventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, event: AuditEvent) -> None:
        ev_uuid = uuid.UUID(event.event_id)
        s_uuid = uuid.UUID(event.session_id)

        stmt = select(AuditEventORM).where(AuditEventORM.id == ev_uuid)
        res = await self._session.execute(stmt)
        orm = res.scalar_one_or_none()

        if not orm:
            orm = AuditEventORM(
                id=ev_uuid,
                session_id=s_uuid,
                assessment_id=event.assessment_id,
                event_type=event.event_type,
                step_order=event.step_order,
                stage_name=event.stage_name,
                payload_json=event.payload,
                invocation_details=event.invocation.to_dict() if event.invocation else {},
                metadata_json=event.metadata.to_dict() if event.metadata else {},
                timestamp=event.timestamp,
            )
            self._session.add(orm)

    async def list_by_session_id(self, session_id: str) -> List[AuditEvent]:
        try:
            s_uuid = uuid.UUID(session_id)
        except ValueError:
            return []

        stmt = (
            select(AuditEventORM)
            .where(AuditEventORM.session_id == s_uuid)
            .order_by(AuditEventORM.step_order)
        )
        res = await self._session.execute(stmt)
        return [self._to_domain(o) for o in res.scalars().all()]

    def _to_domain(self, orm: AuditEventORM) -> AuditEvent:
        inv_dict = orm.invocation_details or {}
        inv = (
            PipelineInvocation(
                subsystem=inv_dict.get("subsystem", "GENERAL"),
                provider=inv_dict.get("provider", "INTERNAL"),
                model_name=inv_dict.get("model_name", "standard"),
                version=inv_dict.get("version", "1.0"),
                latency_ms=inv_dict.get("latency_ms", 0.0),
                token_usage=inv_dict.get("token_usage", {}),
                checksum=inv_dict.get("checksum", ""),
            )
            if inv_dict
            else None
        )

        meta_dict = orm.metadata_json or {}
        meta = AuditMetadata(tags=meta_dict.get("tags", {})) if meta_dict else None

        return AuditEvent(
            event_id=str(orm.id),
            session_id=str(orm.session_id),
            assessment_id=orm.assessment_id,
            event_type=orm.event_type,
            step_order=orm.step_order,
            stage_name=orm.stage_name,
            payload=orm.payload_json or {},
            invocation=inv,
            metadata=meta,
            timestamp=orm.timestamp,
        )


class DecisionRecordRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, record: DecisionRecord) -> None:
        rec_uuid = uuid.UUID(record.record_id)
        stmt = select(DecisionRecordORM).where(DecisionRecordORM.id == rec_uuid)
        res = await self._session.execute(stmt)
        orm = res.scalar_one_or_none()

        if not orm:
            orm = DecisionRecordORM(
                id=rec_uuid,
                decision_id=record.decision_id,
                assessment_id=record.assessment_id,
                decision_type=record.decision_type,
                input_data_json=record.input_data,
                output_decision_json=record.output_decision,
                score_explanations_json=[se.to_dict() for se in record.score_explanations],
                evidence_references_json=[er.to_dict() for er in record.evidence_references],
                pipeline_invocation_json=record.pipeline_invocation.to_dict() if record.pipeline_invocation else {},
                reproducible_hash=record.reproducible_hash,
                recorded_at=record.recorded_at,
            )
            self._session.add(orm)

    async def get_by_decision_id(self, decision_id: str) -> Optional[DecisionRecord]:
        stmt = select(DecisionRecordORM).where(DecisionRecordORM.decision_id == decision_id)
        res = await self._session.execute(stmt)
        orm = res.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    def _to_domain(self, orm: DecisionRecordORM) -> DecisionRecord:
        se_list = [
            ScoreExplanation(
                framework_name=d.get("framework_name", ""),
                construct_name=d.get("construct_name", ""),
                raw_score=d.get("raw_score", 0.0),
                normalized_score=d.get("normalized_score", 0.0),
                weight=d.get("weight", 1.0),
                scoring_policy_id=d.get("scoring_policy_id", ""),
                confidence=d.get("confidence", 0.0),
            )
            for d in (orm.score_explanations_json or [])
        ]

        er_list = [
            EvidenceReference(
                evidence_id=d.get("evidence_id", ""),
                construct_name=d.get("construct_name", ""),
                verbatim_quote=d.get("verbatim_quote", ""),
                behavioral_indicator=d.get("behavioral_indicator", ""),
                confidence=d.get("confidence", 0.0),
                evidence_type=d.get("evidence_type", "VERBATIM"),
            )
            for d in (orm.evidence_references_json or [])
        ]

        inv_d = orm.pipeline_invocation_json or {}
        inv = (
            PipelineInvocation(
                subsystem=inv_d.get("subsystem", "SCORING"),
                provider=inv_d.get("provider", "ENGINE"),
                model_name=inv_d.get("model_name", "Scorer"),
                version=inv_d.get("version", "1.0"),
                latency_ms=inv_d.get("latency_ms", 0.0),
            )
            if inv_d
            else None
        )

        rec = DecisionRecord(
            decision_id=orm.decision_id,
            assessment_id=orm.assessment_id,
            decision_type=orm.decision_type,
            input_data=orm.input_data_json or {},
            output_decision=orm.output_decision_json or {},
            score_explanations=se_list,
            evidence_references=er_list,
            pipeline_invocation=inv,
            record_id=str(orm.id),
            recorded_at=orm.recorded_at,
        )
        rec.reproducible_hash = orm.reproducible_hash
        return rec
