from typing import Any, Dict, Optional, Tuple
from app.core.logging import logger
from app.domain.entities.assessment_session import AssessmentSession
from app.domain.interfaces.subsystems import IScoringEngine
from app.application.construct_engine.models import ConstructEvaluationSet
from app.application.scoring_engine.calculator import ConstructScoreCalculator
from app.application.scoring_engine.normalizer import ScoreNormalizer
from app.application.scoring_engine.calibration import CalibrationEngine
from app.application.scoring_engine.weighting import WeightingEngine
from app.application.scoring_engine.reliability import ReliabilityEstimator
from app.application.scoring_engine.decision_engine import DecisionEngine
from app.application.scoring_engine.builder import AssessmentScoreBuilder
from app.application.scoring_engine.validator import ScoreValidator
from app.application.scoring_engine.publisher import ScoringEventPublisher
from app.application.scoring_engine.models import AssessmentScoreSet, ConstructScore, CompositeScore
from app.domain.exceptions.scoring_exceptions import ScoringFailure



class PsychometricScoringDecisionEngine(IScoringEngine):
    """Facade for Psychometric Scoring & Decision Engine (PSDE) implementing IScoringEngine.
    Transforms ConstructEvaluationSet objects into immutable AssessmentScoreSet aggregates.
    Calculates deterministic raw scores, normalizes, calibrates, weights, estimates reliability,
    and generates assessment-level decisions.
    DOES NOT RECOMMEND CAREERS OR RENDER REPORT UI!
    """

    def __init__(
        self,
        calculator: Optional[ConstructScoreCalculator] = None,
        normalizer: Optional[ScoreNormalizer] = None,
        calibration: Optional[CalibrationEngine] = None,
        weighting: Optional[WeightingEngine] = None,
        reliability_estimator: Optional[ReliabilityEstimator] = None,
        decision_engine: Optional[DecisionEngine] = None,
        builder: Optional[AssessmentScoreBuilder] = None,
        validator: Optional[ScoreValidator] = None,
        publisher: Optional[ScoringEventPublisher] = None,
    ):
        self.calculator = calculator or ConstructScoreCalculator()
        self.normalizer = normalizer or ScoreNormalizer()
        self.calibration = calibration or CalibrationEngine()
        self.weighting = weighting or WeightingEngine()
        self.reliability_estimator = reliability_estimator or ReliabilityEstimator()
        self.decision_engine = decision_engine or DecisionEngine()
        self.builder = builder or AssessmentScoreBuilder()
        self.validator = validator or ScoreValidator()
        self.publisher = publisher or ScoringEventPublisher()
        from app.application.evidence_engine.anchor_evaluator import AnchorEvaluator
        self.anchor_evaluator = AnchorEvaluator()

    async def compute_speaking_assessment_scores(
        self,
        session: AssessmentSession,
        scenario: Any,
        candidate_responses: Dict[str, Any],
    ) -> Tuple[AssessmentScoreSet, Dict[str, Any]]:
        """Evaluates canonical 3-stage speaking assessment (SQ1, SQ2, SQ3), executes
        rubric & fluency scoring, aggregates construct scores, and compiles deterministic report.
        """
        logger.info(f"[PSDE FACADE] Computing speaking assessment scores for session '{session.session_id}'")
        from app.domain.assessment.speaking_canonical_config import CANONICAL_SPEAKING_SPECS

        narrative = getattr(scenario, "narrative", getattr(scenario, "description", ""))
        scenario_context = f"{scenario.title}\n{narrative}"

        question_eval_results = []
        question_scores: Dict[str, float] = {}

        # 1. Evaluate each canonical speaking prompt (SQ1, SQ2, SQ3)
        for prompt in scenario.speaking_prompts:
            q_id = prompt.question_id
            resp_data = candidate_responses.get(q_id) or candidate_responses.get(prompt.prompt_id, {})
            
            transcript_text = resp_data.get("transcript_text", "")
            duration_seconds = resp_data.get("duration_seconds")
            audio_file_url = resp_data.get("audio_file_url")
            wps = resp_data.get("words_per_second")
            pause_ratio = resp_data.get("pause_ratio")

            eval_res = await self.anchor_evaluator.evaluate_question(
                prompt=prompt,
                scenario_context=scenario_context,
                transcript_text=transcript_text,
                duration_seconds=duration_seconds,
                audio_file_url=audio_file_url,
                words_per_second=wps,
                pause_ratio=pause_ratio,
            )
            question_eval_results.append(eval_res.to_dict())
            question_scores[q_id] = eval_res.question_score

        sq1 = question_scores.get("SQ1", 0.0)
        sq2 = question_scores.get("SQ2", 0.0)
        sq3 = question_scores.get("SQ3", 0.0)

        # 2. Construct Aggregation & Final Speaking Score
        construct_scores_raw, final_speaking_score = self.weighting.aggregate_speaking_construct_scores(
            sq1_score=sq1, sq2_score=sq2, sq3_score=sq3
        )

        # 3. Generate Deterministic Candidate Report
        candidate_report = self.decision_engine.generate_candidate_report(
            construct_scores=construct_scores_raw,
            final_speaking_score=final_speaking_score,
            question_results=question_eval_results,
        )

        # 4. Construct CompositeScore & ConstructScore entities
        composite = CompositeScore(
            composite_name="FINAL_SPEAKING_SCORE",
            score=final_speaking_score,
            calculation_method="CANONICAL_SPEAKING_AGGREGATION",
            supporting_constructs=list(construct_scores_raw.keys()),
        )
        decision = self.decision_engine.generate_decision(composite)
        reliability = self.reliability_estimator.estimate_reliability(len(construct_scores_raw))

        construct_scores: Dict[str, ConstructScore] = {
            c_name: ConstructScore(
                construct=c_name,
                raw_score=c_val,
                normalized_score=c_val,
                weight=self.weighting.CANONICAL_SPEAKING_WEIGHTS.get(c_name, 1.0),
                confidence=0.95,
                calibration_version=self.calibration.calibration_version,
            )
            for c_name, c_val in construct_scores_raw.items()
        }

        # 5. Build and validate score set
        score_set = self.builder.build_score_set(
            session_id=session.session_id,
            scenario_id=session.scenario_id,
            construct_scores=construct_scores,
            composite=composite,
            decision=decision,
            reliability=reliability,
        )

        # Register metadata in session
        session.metadata["speaking_evaluations"] = question_eval_results
        session.metadata["candidate_report"] = candidate_report
        session.metadata["overall_construct_scores"] = construct_scores_raw
        session.metadata["final_speaking_score"] = final_speaking_score

        return score_set, candidate_report


    async def compute_assessment_scores(
        self,
        session: AssessmentSession,
        evaluation_set: ConstructEvaluationSet,
    ) -> AssessmentScoreSet:
        """Computes standardized psychometric assessment scores and decision aggregates."""
        logger.info(f"[PSDE FACADE] Computing assessment scores for session '{session.session_id}'")
        await self.publisher.publish_started(session.session_id, session.scenario_id)

        try:
            # 1. Calculate Raw Scores
            raw_scores = self.calculator.calculate_raw_scores(evaluation_set)
            await self.publisher.publish_construct_scores_calculated(session.session_id, len(raw_scores))

            # 2. Normalize Scores (0-100 Scale)
            norm_scores = self.normalizer.normalize_scores(raw_scores, scale_type="SCALE_100")
            await self.publisher.publish_normalization_completed(session.session_id, "SCALE_100")

            # 3. Apply Calibration Adjustments
            cal_scores = self.calibration.calibrate_scores(norm_scores)
            await self.publisher.publish_calibration_completed(session.session_id, self.calibration.calibration_version)

            # 4. Apply Construct Weights & Compute Weighted Composite
            weights, composite = self.weighting.compute_weighted_composite(cal_scores)
            await self.publisher.publish_weighting_completed(session.session_id, composite.score)

            # 5. Estimate Psychometric Reliability
            reliability = self.reliability_estimator.estimate_reliability(len(raw_scores))
            await self.publisher.publish_reliability_estimated(session.session_id, reliability.reliability_estimate)

            # 6. Generate Assessment Competency Decision
            decision = self.decision_engine.generate_decision(composite)
            await self.publisher.publish_decision_generated(session.session_id, decision.decision_band)

            # Construct individual ConstructScore domain objects
            construct_scores: Dict[str, ConstructScore] = {
                c_name: ConstructScore(
                    construct=c_name,
                    raw_score=raw_scores[c_name],
                    normalized_score=cal_scores[c_name],
                    weight=weights.get(c_name, 1.0),
                    confidence=0.95,
                    calibration_version=self.calibration.calibration_version,
                )
                for c_name in raw_scores
            }

            # 7. Build Immutable AssessmentScoreSet Aggregate
            score_set = self.builder.build_score_set(
                session_id=session.session_id,
                scenario_id=session.scenario_id,
                construct_scores=construct_scores,
                composite=composite,
                decision=decision,
                reliability=reliability,
            )

            # 8. Validate Score Set
            self.validator.validate_score_set(score_set)
            await self.publisher.publish_validated(session.session_id, "VALIDATED")

            # Register construct scores back into AssessmentSession metadata
            session.metadata["overall_construct_scores"] = {
                c_name: c_score.normalized_score for c_name, c_score in construct_scores.items()
            }

            await self.publisher.publish_completed(session.session_id, composite.score, decision.decision_band)
            logger.info(f"[PSDE FACADE] Completed scoring for session '{session.session_id}'. Composite: {composite.score}, Band: {decision.decision_band}")

            return score_set

        except Exception as e:
            await self.publisher.publish_failed(session.session_id, str(e))
            logger.error(f"[PSDE FACADE] Scoring failed for session '{session.session_id}': {str(e)}")
            raise ScoringFailure(session.session_id, str(e))

    async def calculate_construct_scores(self, session: AssessmentSession) -> Dict[str, float]:
        """Implementation of IScoringEngine abstract interface method."""
        return session.metadata.get("overall_construct_scores", {})
