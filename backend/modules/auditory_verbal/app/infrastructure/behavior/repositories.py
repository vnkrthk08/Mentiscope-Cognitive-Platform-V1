import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.behavior.entities.behavior_evidence import BehaviorEvidence
from app.domain.behavior.entities.behavior_observation import BehaviorObservation
from app.domain.behavior.entities.evidence_source import EvidenceSource
from app.domain.behavior.value_objects.quote_reference import QuoteReference
from app.domain.behavior.value_objects.evidence_confidence import EvidenceConfidence
from app.domain.behavior.value_objects.evidence_metadata import EvidenceMetadata
from app.infrastructure.behavior.orm_models import BehaviorEvidenceORM, BehaviorMetricORM


class BehaviorMapper:
    @staticmethod
    def to_domain(orm: BehaviorEvidenceORM) -> BehaviorEvidence:
        obs_list = []
        for o in orm.behavior_observations:
            quotes = []
            for q in o["supporting_quotes"]:
                quotes.append(
                    QuoteReference(
                        quote=q["quote"],
                        start_word_index=q["start_word_index"],
                        end_word_index=q["end_word_index"],
                        start_time=q["start_time"],
                        end_time=q["end_time"],
                    )
                )
            
            c = o["confidence"]
            conf = EvidenceConfidence(
                overall=c["overall"],
                supporting_score=c["supporting_score"],
                consistency_score=c["consistency_score"],
            )

            obs_list.append(
                BehaviorObservation(
                    observation_id=o["observation_id"],
                    behavior_type=o["behavior_type"],
                    description=o["description"],
                    supporting_quotes=quotes,
                    confidence=conf,
                    linked_constructs=o.get("linked_constructs", []),
                )
            )

        src_list = []
        for s in orm.evidence_sources:
            ts = datetime.fromisoformat(s["timestamp"]) if isinstance(s["timestamp"], str) else s["timestamp"]
            src_list.append(
                EvidenceSource(
                    source_type=s["source_type"],
                    source_id=s["source_id"],
                    provider=s["provider"],
                    timestamp=ts,
                )
            )

        m = orm.metadata_json
        meta = EvidenceMetadata(
            pipeline_version=m["pipeline_version"],
            model_version=m["model_version"],
            created_at=datetime.fromisoformat(m["created_at"]) if isinstance(m["created_at"], str) else m["created_at"],
        )

        return BehaviorEvidence(
            evidence_id=str(orm.id),
            transcript_id=str(orm.transcript_id),
            prompt_execution_id=str(orm.prompt_execution_id),
            candidate_id=orm.candidate_id,
            assessment_id=str(orm.assessment_id),
            scenario_id=str(orm.scenario_id),
            construct_candidates=orm.construct_candidates,
            behavior_observations=obs_list,
            evidence_sources=src_list,
            overall_confidence=orm.overall_confidence,
            metadata=meta,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    @staticmethod
    def to_orm(domain: BehaviorEvidence) -> BehaviorEvidenceORM:
        obs_payload = []
        for o in domain.behavior_observations:
            quotes = []
            for q in o.supporting_quotes:
                quotes.append(
                    {
                        "quote": q.quote,
                        "start_word_index": q.start_word_index,
                        "end_word_index": q.end_word_index,
                        "start_time": q.start_time,
                        "end_time": q.end_time,
                    }
                )
            
            obs_payload.append(
                {
                    "observation_id": o.observation_id,
                    "behavior_type": o.behavior_type,
                    "description": o.description,
                    "supporting_quotes": quotes,
                    "confidence": {
                        "overall": o.confidence.overall,
                        "supporting_score": o.confidence.supporting_score,
                        "consistency_score": o.confidence.consistency_score,
                    },
                    "linked_constructs": o.linked_constructs,
                }
            )

        src_payload = []
        for s in domain.evidence_sources:
            src_payload.append(
                {
                    "source_type": s.source_type,
                    "source_id": s.source_id,
                    "provider": s.provider,
                    "timestamp": s.timestamp.isoformat(),
                }
            )

        meta_payload = {
            "pipeline_version": domain.metadata.pipeline_version,
            "model_version": domain.metadata.model_version,
            "created_at": domain.metadata.created_at.isoformat(),
        }

        return BehaviorEvidenceORM(
            id=uuid.UUID(domain.evidence_id),
            transcript_id=uuid.UUID(domain.transcript_id),
            prompt_execution_id=uuid.UUID(domain.prompt_execution_id),
            candidate_id=domain.candidate_id,
            assessment_id=uuid.UUID(domain.assessment_id),
            scenario_id=uuid.UUID(domain.scenario_id),
            construct_candidates=domain.construct_candidates,
            behavior_observations=obs_payload,
            evidence_sources=src_payload,
            overall_confidence=domain.overall_confidence,
            metadata_json=meta_payload,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
        )


class BehaviorRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, evidence_id: str) -> Optional[BehaviorEvidence]:
        try:
            eid = uuid.UUID(evidence_id)
        except ValueError:
            return None
        orm = await self.session.get(BehaviorEvidenceORM, eid)
        return BehaviorMapper.to_domain(orm) if orm else None

    async def get_by_transcript_id(self, transcript_id: str) -> List[BehaviorEvidence]:
        try:
            tid = uuid.UUID(transcript_id)
        except ValueError:
            return []
        result = await self.session.execute(
            select(BehaviorEvidenceORM).where(BehaviorEvidenceORM.transcript_id == tid)
        )
        return [BehaviorMapper.to_domain(orm) for orm in result.scalars().all()]

    async def save(self, evidence: BehaviorEvidence) -> BehaviorEvidence:
        orm = BehaviorMapper.to_orm(evidence)
        existing = await self.session.get(BehaviorEvidenceORM, orm.id)
        if existing:
            existing.construct_candidates = orm.construct_candidates
            existing.behavior_observations = orm.behavior_observations
            existing.evidence_sources = orm.evidence_sources
            existing.overall_confidence = orm.overall_confidence
            existing.metadata_json = orm.metadata_json
            existing.updated_at = datetime.now(timezone.utc)
            orm = existing
        else:
            self.session.add(orm)
        await self.session.flush()
        return BehaviorMapper.to_domain(orm)

    async def save_metric(self, metric_orm: BehaviorMetricORM) -> None:
        self.session.add(metric_orm)
        await self.session.flush()
