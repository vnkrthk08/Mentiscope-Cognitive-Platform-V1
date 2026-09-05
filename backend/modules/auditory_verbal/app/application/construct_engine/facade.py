from typing import Any, Dict, Optional
from app.core.logging import logger
from app.domain.entities.assessment_session import AssessmentSession
from app.application.evidence_engine.models import BehavioralEvidenceSet
from app.application.construct_engine.grouping_service import ConstructGroupingService
from app.application.construct_engine.coordinator import ConstructEvaluationCoordinator
from app.application.construct_engine.builder import ConstructEvaluationBuilder
from app.application.construct_engine.validator import ConstructValidator
from app.application.construct_engine.publisher import ConstructEventPublisher
from app.application.construct_engine.models import ConstructEvaluationSet
from app.domain.exceptions.construct_exceptions import PsychometricEvaluationFailure


class PsychometricConstructEvaluationEngine:
    """Facade for Psychometric Construct Evaluation Engine (PCEE).
    Transforms BehavioralEvidenceSet objects into immutable ConstructEvaluationSet aggregates.
    Communicates with LLMs EXCLUSIVELY through AI Prompt Orchestration Service (APOS).
    DOES NOT CALCULATE NUMERICAL SCORES, RANK CANDIDATES, OR GENERATE REPORTS!
    """

    def __init__(
        self,
        grouping_service: Optional[ConstructGroupingService] = None,
        coordinator: Optional[ConstructEvaluationCoordinator] = None,
        builder: Optional[ConstructEvaluationBuilder] = None,
        validator: Optional[ConstructValidator] = None,
        publisher: Optional[ConstructEventPublisher] = None,
    ):
        self.grouping_service = grouping_service or ConstructGroupingService()
        self.coordinator = coordinator or ConstructEvaluationCoordinator()
        self.builder = builder or ConstructEvaluationBuilder()
        self.validator = validator or ConstructValidator()
        self.publisher = publisher or ConstructEventPublisher()

    async def evaluate_constructs(
        self,
        session: AssessmentSession,
        evidence_set: BehavioralEvidenceSet,
    ) -> ConstructEvaluationSet:
        """Evaluates psychological constructs from a BehavioralEvidenceSet aggregate."""
        logger.info(f"[PCEE FACADE] Evaluating construct evidence for session '{session.session_id}'")
        await self.publisher.publish_started(session.session_id, session.scenario_id)

        try:
            # 1. Group Evidence by Construct
            grouped_evidence = self.grouping_service.group_evidence_by_construct(evidence_set)
            summaries = self.grouping_service.build_evidence_summaries(grouped_evidence)
            await self.publisher.publish_evidence_loaded(session.session_id, len(evidence_set.evidence_items))

            # 2. Build APOS Prompt Variables
            c_names = ", ".join(grouped_evidence.keys())
            obs_text = " | ".join([s.observation_summary for s in summaries])
            variables = {
                "scenario_title": session.scenario_id,
                "construct_name": c_names,
                "evidence_summary": obs_text,
            }

            # 3. Request Construct Evaluation through APOS
            await self.publisher.publish_prompt_requested(session.session_id, "CONSTRUCT_EVALUATION_PROMPT")
            apos_result = await self.coordinator.evaluate_construct_via_apos(variables)
            await self.publisher.publish_prompt_completed(session.session_id, "CONSTRUCT_EVALUATION_PROMPT", apos_result.latency_ms)

            # 4. Build Immutable ConstructEvaluationSet Aggregate
            eval_set = self.builder.build_evaluation_set(
                session_id=session.session_id,
                scenario_id=session.scenario_id,
                apos_result=apos_result,
                summaries=summaries,
            )

            # 5. Validate Evaluation Set
            self.validator.validate_evaluation_set(eval_set)
            await self.publisher.publish_validated(session.session_id, len(eval_set.construct_evaluations))
            await self.publisher.publish_stored(session.session_id, eval_set.evaluation_set_id)

            await self.publisher.publish_completed(session.session_id, len(eval_set.construct_evaluations), eval_set.construct_evaluations[0].evaluation_confidence if eval_set.construct_evaluations else 0.95)
            logger.info(f"[PCEE FACADE] Completed construct evaluation for session '{session.session_id}'. Evaluated {len(eval_set.construct_evaluations)} constructs.")

            return eval_set

        except Exception as e:
            await self.publisher.publish_failed(session.session_id, str(e))
            logger.error(f"[PCEE FACADE] Construct evaluation failed for session '{session.session_id}': {str(e)}")
            raise PsychometricEvaluationFailure(session.session_id, str(e))
