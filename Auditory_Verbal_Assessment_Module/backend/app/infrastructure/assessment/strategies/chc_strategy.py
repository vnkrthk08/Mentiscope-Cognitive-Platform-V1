from typing import List
from app.domain.construct.entities.construct_profile import ConstructProfile
from app.domain.assessment.entities.framework_result import FrameworkResult
from app.domain.assessment.entities.score_breakdown import ScoreBreakdown
from app.domain.assessment.entities.scoring_policy import ScoringPolicy
from app.domain.assessment.value_objects.score_reference import ScoreReference
from app.infrastructure.assessment.strategies.framework_strategy import FrameworkScoringStrategy
from app.infrastructure.assessment.normalization.linear_strategy import LinearNormalization
from app.infrastructure.assessment.normalization.percentile_strategy import PercentileNormalization
from app.infrastructure.assessment.normalization.decile_strategy import DecileNormalization


class CHCStrategy(FrameworkScoringStrategy):
    """Calculates cognitive ability scores based on CHC constructs evaluations."""

    def calculate(self, profiles: List[ConstructProfile], policy: ScoringPolicy) -> FrameworkResult:
        chc_profiles = [p for p in profiles if p.framework.upper() == "CHC"]
        if not chc_profiles:
            raise ValueError("No CHC profiles available for scoring.")

        # Resolve normalizer strategy
        norm_method = policy.normalization_method.upper()
        if norm_method == "PERCENTILE":
            normalizer = PercentileNormalization()
        elif norm_method == "DECILE":
            normalizer = DecileNormalization()
        else:
            normalizer = LinearNormalization()

        breakdowns = []
        raw_sum = 0.0
        conf_sum = 0.0
        evidence_count = 0

        for p in chc_profiles:
            # Raw score based on construct confidence score and weight config
            weight = policy.weight_configuration.get(p.construct_name, 1.0)
            raw_score = p.confidence.confidence_score * weight
            norm_score = normalizer.normalize(p.confidence.confidence_score)

            raw_sum += raw_score
            conf_sum += p.confidence.confidence_score
            evidence_count += p.confidence.evidence_count

            # Trace references
            refs = [
                ScoreReference(
                    construct_evaluation_id=p.supporting_observations[0].reference_id,
                    behavior_evidence_id=p.supporting_observations[0].reference_id,
                    prompt_execution_id="default-exec",
                    transcript_id="default-trans",
                )
                for r in p.supporting_observations
            ]

            breakdowns.append(
                ScoreBreakdown(
                    construct=p.construct_name,
                    raw_score=raw_score,
                    normalized_score=norm_score,
                    confidence=p.confidence.confidence_score,
                    support_strength=p.confidence.support_strength,
                    evidence_count=p.confidence.evidence_count,
                    references=refs,
                )
            )

        avg_raw = raw_sum / len(chc_profiles)
        avg_conf = conf_sum / len(chc_profiles)
        norm_avg = normalizer.normalize(avg_conf)

        summary = f"Scored CHC framework across {len(chc_profiles)} active constructs."

        return FrameworkResult(
            framework="CHC",
            raw_score=avg_raw,
            normalized_score=norm_avg,
            confidence=avg_conf,
            construct_results=breakdowns,
            supporting_evidence_count=evidence_count,
            policy_version=policy.version,
            summary=summary,
        )

    def validate(self, profiles: List[ConstructProfile], policy: ScoringPolicy) -> List[str]:
        chc_profiles = [p for p in profiles if p.framework.upper() == "CHC"]
        errors = []
        for p in chc_profiles:
            if p.confidence.confidence_score < 0.0 or p.confidence.confidence_score > 1.0:
                errors.append(f"CHC construct '{p.construct_name}' score must range between 0.0 and 1.0.")
        return errors
pre=1.0
