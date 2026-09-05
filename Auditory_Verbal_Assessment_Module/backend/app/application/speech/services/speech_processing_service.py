import uuid
import asyncio
from datetime import datetime, timezone
from typing import Tuple, Dict, Any
from fastapi import HTTPException, status
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.domain.speech.entities.transcript import Transcript
from app.domain.speech.entities.transcription_job import TranscriptionJob
from app.domain.speech.value_objects.provider_result import ProviderResult
from app.domain.speech.value_objects.transcript_metadata import TranscriptMetadata
from app.infrastructure.speech.strategies.provider_selection import ProviderSelectionStrategy
from app.infrastructure.speech.circuit_breaker import breaker_pool
from app.infrastructure.speech.retry_policy import execute_with_retry, TransientProviderError
from app.infrastructure.speech.normalizer import TranscriptNormalizer
from app.infrastructure.speech.metrics import metrics_tracker, SpeechMetric
from app.infrastructure.speech.orm_models import SpeechMetricORM
from app.application.speech.events import speech_events
from app.domain.media.value_objects.processing_status import ProcessingStatus


class SpeechProcessingService:
    """Core Speech-to-Text orchestrator managing provider selection, resilience, and normalization."""

    @classmethod
    async def create_transcription_job(
        cls, asset_id: str, selection_policy: str, candidate_id: str
    ) -> Tuple[str, str]:
        # 1. Fetch and validate AudioAsset and session ownership
        async with UnitOfWork() as uow:
            asset = await uow.audio_assets.get_by_id(asset_id)
            if not asset:
                raise HTTPException(status_code=404, detail="Audio asset registration not found.")

            # Validate processing state
            if asset.processing_status != ProcessingStatus.QUEUED:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Audio asset cannot be transcribed in its current state '{asset.processing_status.value}' (must be QUEUED).",
                )

            # Validate ownership
            if asset.candidate_id != candidate_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Unauthorized candidate asset ownership.",
                )

            # Resolve target provider name
            duration = asset.audio_metadata.duration_seconds if asset.audio_metadata else 0.0
            provider_name, _ = ProviderSelectionStrategy.resolve_provider(selection_policy, duration)

            # Register transcription job
            job_id = str(uuid.uuid4())
            job = TranscriptionJob(
                job_id=job_id,
                asset_id=asset_id,
                provider=provider_name,
                status="PENDING",
            )
            await uow.transcription_jobs.save(job)
            await uow.commit()

        # 2. Trigger asynchronous background transcription pipeline execution
        asyncio.create_task(cls._execute_transcription_pipeline(job_id))

        return job_id, provider_name

    @classmethod
    async def _execute_transcription_pipeline(cls, job_id: str) -> None:
        """Asynchronous background pipeline execution."""
        # 1. Load job aggregate details
        async with UnitOfWork() as uow:
            job = await uow.transcription_jobs.get_by_id(job_id)
            if not job:
                return
            job.start()
            await uow.transcription_jobs.save(job)
            
            # Fetch corresponding AudioAsset info
            asset = await uow.audio_assets.get_by_id(job.asset_id)
            if not asset:
                job.fail()
                await uow.transcription_jobs.save(job)
                await uow.commit()
                return
            
            await uow.commit()

        # Update processing_status on AudioAsset to PROCESSING
        async with UnitOfWork() as uow:
            asset_entity = await uow.audio_assets.get_by_id(job.asset_id)
            asset_entity.transition_to(ProcessingStatus.PROCESSING)
            await uow.audio_assets.save(asset_entity)
            await uow.commit()

        provider_name = job.provider.lower()
        breaker = breaker_pool.get(provider_name)
        if not breaker:
            breaker = breaker_pool["whisper"]

        start_time = datetime.now(timezone.utc)

        try:
            # 2. Execute transcription wrapping Circuit Breaker and Exponential Retry Policy
            async def call_transcribe() -> Dict[str, Any]:
                from app.infrastructure.speech.providers.provider_registry import speech_registry
                prov = speech_registry.get_provider(provider_name)
                # Fetch audio bytes from mock/location (simulate S3 download or mock values)
                mock_audio_data = b"MOCK_WAV_BYTES_DATA"
                return await prov.transcribe(mock_audio_data)

            async def call_with_circuit_breaker() -> Dict[str, Any]:
                return await breaker.execute(call_transcribe)

            # Trigger retry policy execution
            raw_response = await execute_with_retry(call_with_circuit_breaker, max_retries=3)

            # 3. Normalize raw output parameters
            norm_text, words, conf_score, lang = TranscriptNormalizer.normalize(
                provider_name, raw_response
            )

            # Calculate processing statistics
            end_time = datetime.now(timezone.utc)
            duration_ms = int((end_time - start_time).total_seconds() * 1000)

            # Estimate cost
            from app.infrastructure.speech.providers.provider_registry import speech_registry
            provider_inst = speech_registry.get_provider(provider_name)
            est_dur = asset.audio_metadata.duration_seconds if asset.audio_metadata else 5.2
            estimated_cost = provider_inst.estimate_cost(est_dur)

            # Hydrate aggregates
            prov_result = ProviderResult(
                provider_name=provider_name,
                provider_version="1.0.0",
                model_name="default-model",
                request_id=raw_response.get("metadata", {}).get("request_id", str(uuid.uuid4())),
                processing_time=raw_response.get("api_latency", float(duration_ms)) / 1000.0,
                api_latency=raw_response.get("api_latency", 100.0),
                estimated_cost=estimated_cost,
                billing_units=1,
                raw_metadata=raw_response,
            )

            meta = TranscriptMetadata(
                normalization_version="1.0.0",
                provider_version="1.0.0",
                processing_pipeline_version="1.0.0",
            )

            transcript_id = str(uuid.uuid4())
            transcript = Transcript(
                transcript_id=transcript_id,
                asset_id=asset.asset_id,
                session_id=asset.session_id,
                assessment_id=asset.assessment_id,
                candidate_id=asset.candidate_id,
                provider_result=prov_result,
                language=lang,
                confidence_score=conf_score,
                transcript_metadata=meta,
                transcript_text=norm_text,
                word_timestamps=words,
                processing_duration_ms=duration_ms,
            )

            # 4. Save results to persistence layer and mark completion status
            async with UnitOfWork() as uow:
                # Update job
                db_job = await uow.transcription_jobs.get_by_id(job_id)
                db_job.complete()
                await uow.transcription_jobs.save(db_job)

                # Save transcript
                await uow.speech_transcripts.save(transcript)

                # Update AudioAsset state to COMPLETED
                db_asset = await uow.audio_assets.get_by_id(asset.asset_id)
                db_asset.transition_to(ProcessingStatus.COMPLETED)
                await uow.audio_assets.save(db_asset)

                # Record metrics
                words_count = len(words)
                wps = words_count / (duration_ms / 1000.0) if duration_ms > 0 else 0.0
                metric = SpeechMetric(
                    provider_name=provider_name,
                    latency_ms=raw_response.get("api_latency", 100.0),
                    success=True,
                    processing_time_ms=duration_ms,
                    cost_usd=estimated_cost,
                    words_count=words_count,
                    words_per_second=wps,
                )
                metrics_tracker.record(metric)

                metric_orm = SpeechMetricORM(
                    id=uuid.uuid4(),
                    provider_name=provider_name,
                    latency_ms=raw_response.get("api_latency", 100.0),
                    success=True,
                    processing_time_ms=duration_ms,
                    cost_usd=estimated_cost,
                    words_count=words_count,
                    words_per_second=wps,
                )
                await uow.speech_transcripts.save_metric(metric_orm)
                await uow.commit()

        except Exception as err:
            # Pipeline failure handling
            async with UnitOfWork() as uow:
                db_job = await uow.transcription_jobs.get_by_id(job_id)
                if db_job:
                    db_job.fail()
                    await uow.transcription_jobs.save(db_job)

                # Transition AudioAsset to FAILED state
                db_asset = await uow.audio_assets.get_by_id(asset.asset_id)
                if db_asset:
                    db_asset.transition_to(ProcessingStatus.FAILED)
                    await uow.audio_assets.save(db_asset)

                # Save metric failure
                metric_orm = SpeechMetricORM(
                    id=uuid.uuid4(),
                    provider_name=provider_name,
                    latency_ms=0.0,
                    success=False,
                    processing_time_ms=0.0,
                    cost_usd=0.0,
                    words_count=0,
                    words_per_second=0.0,
                )
                await uow.speech_transcripts.save_metric(metric_orm)
                await uow.commit()
