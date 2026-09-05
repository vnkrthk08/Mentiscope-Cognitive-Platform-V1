import uuid
from datetime import datetime, timezone
from typing import Tuple
from fastapi import HTTPException, status
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.infrastructure.behavior.extractors.behavior_extractor import BehaviorExtractor
from app.infrastructure.behavior.validator import EvidenceValidator
from app.infrastructure.behavior.normalizer import EvidenceNormalizer
from app.infrastructure.behavior.orm_models import BehaviorMetricORM
from app.domain.behavior.entities.evidence_source import EvidenceSource


class BehaviorExtractionService:
    """Application service coordinating behavioral evidence extraction, validation, and quarantine pipelines."""

    @classmethod
    async def extract_behavioral_evidence(
        cls, execution_id: str, candidate_id: str
    ) -> Tuple[str, bool, int]:
        # 1. Fetch PromptExecution and validate candidate ownership
        async with UnitOfWork() as uow:
            execution = await uow.llm_prompts.get_by_id(execution_id)
            if not execution:
                raise HTTPException(status_code=404, detail="Prompt execution record not found.")

            if execution.status != "COMPLETED" or not execution.response:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Prompt execution must be COMPLETED before extraction (current status: {execution.status}).",
                )

            # Resolve transcript to check ownership
            transcript = await uow.speech_transcripts.get_by_id(execution.transcript_id)
            if not transcript or transcript.candidate_id != candidate_id:
                raise HTTPException(
                    status_code=status.HTTP_430_FORBIDDEN if hasattr(status, "HTTP_430_FORBIDDEN") else status.HTTP_403_FORBIDDEN,
                    detail="Unauthorized candidate execution ownership.",
                )

            assessment_id = transcript.assessment_id
            scenario_id = transcript.assessment_id  # fallback
            transcript_id = transcript.transcript_id

        start_time = datetime.now(timezone.utc)

        # 2. Extract structured observations using extractor rules
        raw_obs = BehaviorExtractor.extract_observations(execution.response.content_normalized)

        # 3. Validate observations (filter low-confidence, empty quotes, and duplicates)
        valid_obs, quarantined_obs = EvidenceValidator.validate_observations(raw_obs)

        # 4. Construct aggregate root and normalize
        sources = [
            EvidenceSource(
                source_type="PROMPT_RESPONSE",
                source_id=execution.response.response_id,
                provider=execution.provider_result.provider_name if execution.provider_result else "unknown",
            )
        ]

        evidence = EvidenceNormalizer.normalize(
            transcript_id=transcript_id,
            execution_id=execution_id,
            candidate_id=candidate_id,
            assessment_id=assessment_id,
            scenario_id=scenario_id,
            observations=valid_obs,
            sources=sources,
        )

        validation_passed = len(quarantined_obs) == 0

        # Calculate metrics
        end_time = datetime.now(timezone.utc)
        duration_ms = float((end_time - start_time).total_seconds() * 1000)

        # Calculate duplicate rate
        total_count = len(raw_obs)
        dup_count = len([o for o, r in quarantined_obs if "Duplicate" in r])
        dup_rate = dup_count / total_count if total_count > 0 else 0.0

        # Save to database
        async with UnitOfWork() as uow:
            await uow.behavior_evidences.save(evidence)

            # Save metrics
            metric = BehaviorMetricORM(
                id=uuid.uuid4(),
                transcript_id=uuid.UUID(transcript_id),
                latency_ms=duration_ms,
                evidence_count=len(valid_obs),
                average_confidence=evidence.overall_confidence,
                duplicate_rate=dup_rate,
                validation_failures=len(quarantined_obs),
            )
            await uow.behavior_evidences.save_metric(metric)
            await uow.commit()

        return evidence.evidence_id, validation_passed, len(valid_obs)
