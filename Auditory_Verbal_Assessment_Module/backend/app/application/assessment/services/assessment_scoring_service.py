import uuid
from datetime import datetime, timezone
from typing import Tuple, List
from fastapi import HTTPException, status
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork
from app.domain.assessment.entities.assessment_result import AssessmentResult
from app.domain.assessment.entities.assessment_report import AssessmentReport
from app.domain.assessment.entities.scoring_policy import ScoringPolicy
from app.domain.assessment.value_objects.scoring_metadata import ScoringMetadata
from app.infrastructure.assessment.strategies.chc_strategy import CHCStrategy
from app.infrastructure.assessment.strategies.riasec_strategy import RIASECStrategy
from app.infrastructure.assessment.strategies.personality_strategy import PersonalityStrategy
from app.infrastructure.assessment.strategies.emotional_regulation_strategy import EmotionalRegulationStrategy
from app.infrastructure.assessment.score_aggregator import ScoreAggregator
from app.infrastructure.assessment.assessment_validator import AssessmentValidator
from app.infrastructure.assessment.report_builder import AssessmentReportBuilder
from app.infrastructure.assessment.orm_models import AssessmentMetricORM


class AssessmentScoringService:
    """Application orchestrator calculating raw/normalized scores and generating explainable reports."""

    @classmethod
    async def generate_report(
        cls, construct_evaluation_id: str, candidate_id: str
    ) -> Tuple[str, str, float]:
        start_time = datetime.now(timezone.utc)

        # 1. Fetch construct evaluation and validate candidate ownership
        async with UnitOfWork() as uow:
            eval_aggregate = await uow.construct_evaluations.get_by_id(construct_evaluation_id)
            if not eval_aggregate:
                raise HTTPException(status_code=404, detail="ConstructEvaluation record not found.")

            if eval_aggregate.candidate_id != candidate_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Unauthorized candidate evaluation ownership.",
                )

            assessment_id = eval_aggregate.assessment_id
            scenario_id = eval_aggregate.scenario_id
            profiles = eval_aggregate.construct_profiles

        # 2. Map strategies and retrieve ScoringPolicies (with automatic seed fallback)
        strategies_map = {
            "CHC": CHCStrategy(),
            "RIASEC": RIASECStrategy(),
            "PERSONALITY": PersonalityStrategy(),
            "EMOTIONAL_REGULATION": EmotionalRegulationStrategy(),
        }

        framework_results = []
        async with UnitOfWork() as uow:
            for fw, strategy in strategies_map.items():
                # Check if profiles have constructs matching this framework
                fw_profiles = [p for p in profiles if p.framework.upper() == fw]
                if not fw_profiles:
                    continue

                # Load or seed policy
                policy = await uow.assessment_reports.get_policy_by_framework(fw)
                if not policy:
                    # Seed policy
                    policy = ScoringPolicy(
                        policy_id=f"policy-{fw.lower()}-v1",
                        framework=fw,
                        policy_name=f"Standard Weighting Policy for {fw}",
                        version="1.0.0",
                        weight_configuration={p.construct_name: 1.0 for p in fw_profiles},
                        normalization_method="LINEAR",
                        confidence_method="AVERAGE",
                    )
                    await uow.assessment_reports.save_policy(policy)

                # Calculate scores via strategy
                fw_res = strategy.calculate(fw_profiles, policy)
                framework_results.append(fw_res)

            await uow.commit()

        if not framework_results:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No constructs matched active scoring frameworks.",
            )

        # 3. Aggregate overall confidence and overall scores
        overall_scores = ScoreAggregator.aggregate_scores(framework_results)
        overall_confidence = ScoreAggregator.aggregate_confidence(framework_results)

        meta = ScoringMetadata(
            framework_version="1.0.0",
            scoring_policy_version="1.0.0",
            pipeline_version="1.0.0",
            engine_version="1.0.0",
        )

        result_id = str(uuid.uuid4())
        result = AssessmentResult(
            result_id=result_id,
            candidate_id=candidate_id,
            assessment_id=assessment_id,
            construct_evaluation_id=construct_evaluation_id,
            framework_results=framework_results,
            overall_scores=overall_scores,
            overall_confidence=overall_confidence,
            scoring_metadata=meta,
        )

        # Validate result
        val_errors = AssessmentValidator.validate_result(result)
        if val_errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Scoring validation errors: {', '.join(val_errors)}",
            )

        # 4. Build and validate AssessmentReport
        report = AssessmentReportBuilder.build_report(result)
        rep_errors = AssessmentValidator.validate_report(report)
        if rep_errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Report validation errors: {', '.join(rep_errors)}",
            )

        end_time = datetime.now(timezone.utc)
        duration_ms = float((end_time - start_time).total_seconds() * 1000)

        # Save to database
        async with UnitOfWork() as uow:
            await uow.assessment_reports.save_result(result)
            await uow.assessment_reports.save_report(report)

            # Record metrics
            metric = AssessmentMetricORM(
                id=uuid.uuid4(),
                report_id=uuid.UUID(report.report_id),
                scoring_latency_ms=duration_ms / 2.0,
                report_latency_ms=duration_ms / 2.0,
                framework_coverage=len(framework_results),
                average_score=sum(overall_scores.values()) / len(overall_scores) if overall_scores else 0.0,
                average_confidence=overall_confidence,
                evidence_utilization=1.0,
            )
            await uow.assessment_reports.save_metric(metric)
            await uow.commit()

        return report.report_id, result_id, overall_confidence
pre=1.0
