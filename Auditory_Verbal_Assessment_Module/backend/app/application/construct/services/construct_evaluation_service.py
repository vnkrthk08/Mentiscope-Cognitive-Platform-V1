import uuid
from datetime import datetime, timezone
from typing import Tuple
from fastapi import HTTPException, status
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.infrastructure.construct.aggregation_engine import EvidenceAggregator
from app.infrastructure.construct.validator import ConstructValidator
from app.infrastructure.construct.orm_models import ConstructMetricORM
from app.domain.construct.entities.construct_evaluation import ConstructEvaluation
from app.domain.construct.value_objects.construct_metadata import ConstructMetadata


class ConstructEvaluationService:
    """Application service orchestrating validated observations maps aggregation and profiles scoring."""

    @classmethod
    async def evaluate_evidence(
        cls, behavior_evidence_id: str, candidate_id: str
    ) -> Tuple[str, int, float]:
        # 1. Fetch BehaviorEvidence and validate candidate ownership
        async with UnitOfWork() as uow:
            evidence = await uow.behavior_evidences.get_by_id(behavior_evidence_id)
            if not evidence:
                raise HTTPException(status_code=404, detail="BehaviorEvidence aggregate not found.")

            if evidence.candidate_id != candidate_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Unauthorized candidate behavior evidence ownership.",
                )

            transcript_id = evidence.transcript_id
            assessment_id = evidence.assessment_id
            scenario_id = evidence.scenario_id
            observations = evidence.behavior_observations

        start_time = datetime.now(timezone.utc)

        # 2. Group observations and construct profiles
        raw_profiles = EvidenceAggregator.aggregate_evidence(observations)

        # 3. Validate profiles via ConstructValidator
        valid_profiles, errors = ConstructValidator.validate_profiles(raw_profiles)
        if errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Construct validation errors: {', '.join(errors)}",
            )

        # 4. Overall confidence (average of valid profiles confidence score)
        overall_conf = 1.0
        if valid_profiles:
            overall_conf = sum(p.confidence.confidence_score for p in valid_profiles) / len(valid_profiles)

        meta = ConstructMetadata(
            framework_version="1.0.0",
            pipeline_version="1.0.0",
        )

        evaluation_id = str(uuid.uuid4())
        evaluation = ConstructEvaluation(
            evaluation_id=evaluation_id,
            behavior_evidence_id=behavior_evidence_id,
            candidate_id=candidate_id,
            assessment_id=assessment_id,
            scenario_id=scenario_id,
            construct_profiles=valid_profiles,
            overall_evaluation_confidence=overall_conf,
            metadata=meta,
        )

        # Calculate metrics
        end_time = datetime.now(timezone.utc)
        duration_ms = float((end_time - start_time).total_seconds() * 1000)

        # Coverage is defined as framework count evaluated
        frameworks_set = {p.framework for p in valid_profiles}
        utilization = len(valid_profiles) / len(observations) if observations else 1.0

        # Save to database
        async with UnitOfWork() as uow:
            await uow.construct_evaluations.save(evaluation)

            # Record metrics
            metric = ConstructMetricORM(
                id=uuid.uuid4(),
                evaluation_id=uuid.UUID(evaluation_id),
                latency_ms=duration_ms,
                construct_coverage=len(frameworks_set),
                evidence_utilization=utilization,
                average_confidence=overall_conf,
                mapping_conflicts=0,
            )
            await uow.construct_evaluations.save_metric(metric)
            await uow.commit()

        return evaluation_id, len(valid_profiles), overall_conf
pre=1.0
