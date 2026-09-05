import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.speech.entities.transcript import Transcript
from app.domain.speech.entities.speaker_segment import SpeakerSegment
from app.domain.speech.entities.transcription_job import TranscriptionJob
from app.domain.speech.value_objects.word_timestamp import WordTimestamp
from app.domain.speech.value_objects.provider_result import ProviderResult
from app.domain.speech.value_objects.confidence_score import ConfidenceScore
from app.domain.speech.value_objects.language import Language
from app.domain.speech.value_objects.transcript_metadata import TranscriptMetadata
from app.infrastructure.speech.orm_models import TranscriptORM, TranscriptionJobORM, SpeechMetricORM


class SpeechMapper:
    @staticmethod
    def to_domain(orm: TranscriptORM) -> Transcript:
        p = orm.provider_result
        prov_vo = ProviderResult(
            provider_name=p["provider_name"],
            provider_version=p["provider_version"],
            model_name=p["model_name"],
            request_id=p["request_id"],
            processing_time=p["processing_time"],
            api_latency=p["api_latency"],
            estimated_cost=p["estimated_cost"],
            billing_units=p["billing_units"],
            raw_metadata=p.get("raw_metadata", {}),
        )

        l = orm.language
        lang_vo = Language(language_code=l["language_code"], confidence=l["confidence"])

        c = orm.confidence_score
        conf_vo = ConfidenceScore(overall_score=c["overall_score"], per_word_scores=c.get("per_word_scores", []))

        m = orm.transcript_metadata
        gen_at = datetime.fromisoformat(m["generated_at"]) if isinstance(m["generated_at"], str) else m["generated_at"]
        meta_vo = TranscriptMetadata(
            normalization_version=m["normalization_version"],
            provider_version=m["provider_version"],
            processing_pipeline_version=m["processing_pipeline_version"],
            generated_at=gen_at,
        )

        words = []
        for w in orm.word_timestamps:
            words.append(
                WordTimestamp(
                    word=w["word"],
                    start_time=w["start_time"],
                    end_time=w["end_time"],
                    confidence=w["confidence"],
                )
            )

        speakers = []
        for s in orm.speaker_segments:
            speakers.append(
                SpeakerSegment(
                    speaker_id=s["speaker_id"],
                    start_time=s["start_time"],
                    end_time=s["end_time"],
                    text=s["text"],
                )
            )

        return Transcript(
            transcript_id=str(orm.id),
            asset_id=str(orm.asset_id),
            session_id=str(orm.session_id),
            assessment_id=str(orm.assessment_id),
            candidate_id=orm.candidate_id,
            provider_result=prov_vo,
            language=lang_vo,
            confidence_score=conf_vo,
            transcript_metadata=meta_vo,
            transcript_text=orm.transcript_text,
            word_timestamps=words,
            speaker_segments=speakers,
            processing_duration_ms=orm.processing_duration_ms,
            created_at=orm.created_at,
            updated_at=orm.updated_at,
        )

    @staticmethod
    def to_orm(domain: Transcript) -> TranscriptORM:
        prov_payload = {
            "provider_name": domain.provider_result.provider_name,
            "provider_version": domain.provider_result.provider_version,
            "model_name": domain.provider_result.model_name,
            "request_id": domain.provider_result.request_id,
            "processing_time": domain.provider_result.processing_time,
            "api_latency": domain.provider_result.api_latency,
            "estimated_cost": domain.provider_result.estimated_cost,
            "billing_units": domain.provider_result.billing_units,
            "raw_metadata": domain.provider_result.raw_metadata,
        }

        lang_payload = {
            "language_code": domain.language.language_code,
            "confidence": domain.language.confidence,
        }

        conf_payload = {
            "overall_score": domain.confidence_score.overall_score,
            "per_word_scores": domain.confidence_score.per_word_scores,
        }

        meta_payload = {
            "normalization_version": domain.transcript_metadata.normalization_version,
            "provider_version": domain.transcript_metadata.provider_version,
            "processing_pipeline_version": domain.transcript_metadata.processing_pipeline_version,
            "generated_at": domain.transcript_metadata.generated_at.isoformat(),
        }

        words_payload = []
        for w in domain.word_timestamps:
            words_payload.append(
                {
                    "word": w.word,
                    "start_time": w.start_time,
                    "end_time": w.end_time,
                    "confidence": w.confidence,
                }
            )

        speakers_payload = []
        for s in domain.speaker_segments:
            speakers_payload.append(
                {
                    "speaker_id": s.speaker_id,
                    "start_time": s.start_time,
                    "end_time": s.end_time,
                    "text": s.text,
                }
            )

        return TranscriptORM(
            id=uuid.UUID(domain.transcript_id),
            asset_id=uuid.UUID(domain.asset_id),
            session_id=uuid.UUID(domain.session_id),
            assessment_id=uuid.UUID(domain.assessment_id),
            candidate_id=domain.candidate_id,
            provider_result=prov_payload,
            language=lang_payload,
            confidence_score=conf_payload,
            transcript_metadata=meta_payload,
            transcript_text=domain.transcript_text,
            word_timestamps=words_payload,
            speaker_segments=speakers_payload,
            processing_duration_ms=domain.processing_duration_ms,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
        )


class SpeechRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, transcript_id: str) -> Optional[Transcript]:
        try:
            tid = uuid.UUID(transcript_id)
        except ValueError:
            return None
        orm = await self.session.get(TranscriptORM, tid)
        return SpeechMapper.to_domain(orm) if orm else None

    async def get_by_asset_id(self, asset_id: str) -> Optional[Transcript]:
        try:
            aid = uuid.UUID(asset_id)
        except ValueError:
            return None
        result = await self.session.execute(
            select(TranscriptORM).where(TranscriptORM.asset_id == aid)
        )
        orm = result.scalars().first()
        return SpeechMapper.to_domain(orm) if orm else None

    async def save(self, transcript: Transcript) -> Transcript:
        orm = SpeechMapper.to_orm(transcript)
        existing = await self.session.get(TranscriptORM, orm.id)
        if existing:
            existing.provider_result = orm.provider_result
            existing.language = orm.language
            existing.confidence_score = orm.confidence_score
            existing.transcript_metadata = orm.transcript_metadata
            existing.transcript_text = orm.transcript_text
            existing.word_timestamps = orm.word_timestamps
            existing.speaker_segments = orm.speaker_segments
            existing.processing_duration_ms = orm.processing_duration_ms
            existing.updated_at = datetime.now(timezone.utc)
            orm = existing
        else:
            self.session.add(orm)
        await self.session.flush()
        return SpeechMapper.to_domain(orm)

    async def save_metric(self, metric_orm: SpeechMetricORM) -> None:
        self.session.add(metric_orm)
        await self.session.flush()


class TranscriptionJobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, job_id: str) -> Optional[TranscriptionJob]:
        try:
            jid = uuid.UUID(job_id)
        except ValueError:
            return None
        orm = await self.session.get(TranscriptionJobORM, jid)
        if not orm:
            return None
        return TranscriptionJob(
            job_id=str(orm.id),
            asset_id=str(orm.asset_id),
            provider=orm.provider,
            status=orm.status,
            retry_count=orm.retry_count,
            created_at=orm.created_at,
            started_at=orm.started_at,
            completed_at=orm.completed_at,
        )

    async def save(self, job: TranscriptionJob) -> TranscriptionJob:
        jid = uuid.UUID(job.job_id)
        existing = await self.session.get(TranscriptionJobORM, jid)
        if existing:
            existing.status = job.status
            existing.retry_count = job.retry_count
            existing.started_at = job.started_at
            existing.completed_at = job.completed_at
            orm = existing
        else:
            orm = TranscriptionJobORM(
                id=jid,
                asset_id=uuid.UUID(job.asset_id),
                provider=job.provider,
                status=job.status,
                retry_count=job.retry_count,
                created_at=job.created_at,
                started_at=job.started_at,
                completed_at=job.completed_at,
            )
            self.session.add(orm)
        await self.session.flush()
        return job
