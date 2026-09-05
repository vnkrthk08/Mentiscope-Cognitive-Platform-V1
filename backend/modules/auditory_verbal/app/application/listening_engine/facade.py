from typing import Any, Dict, Optional
from app.core.logging import logger
from app.domain.entities.assessment_session import AssessmentSession
from app.domain.entities.scenario import Scenario
from app.domain.entities.candidate_response import ListeningResponse
from app.domain.interfaces.executors import IListeningExecutor
from app.application.listening_engine.session import ListeningSession
from app.application.listening_engine.player import ListeningPlayer
from app.application.listening_engine.navigator import ListeningNavigator
from app.application.listening_engine.collector import ListeningResponseCollector
from app.application.listening_engine.validator import ListeningValidator
from app.application.listening_engine.result_builder import ListeningResultBuilder, ListeningSessionResult
from app.application.listening_engine.publisher import ListeningEventPublisher
from app.domain.exceptions.listening_exceptions import ListeningModuleMissing, ListeningSessionFailure


class ListeningAssessmentEngine(IListeningExecutor):
    """Facade for the Listening Assessment Engine (LAE) implementing IListeningExecutor.
    Executes deterministic listening question navigation, audio playback, answer collection,
    and result building. ZERO AI!
    """

    def __init__(
        self,
        player: Optional[ListeningPlayer] = None,
        collector: Optional[ListeningResponseCollector] = None,
        validator: Optional[ListeningValidator] = None,
        result_builder: Optional[ListeningResultBuilder] = None,
        publisher: Optional[ListeningEventPublisher] = None,
    ):
        self.player = player or ListeningPlayer()
        self.collector = collector or ListeningResponseCollector()
        self.validator = validator or ListeningValidator()
        self.result_builder = result_builder or ListeningResultBuilder()
        self.publisher = publisher or ListeningEventPublisher()

    async def execute(self, session: AssessmentSession, scenario: Scenario) -> Dict[str, Any]:
        """Executes complete deterministic listening assessment pipeline for a scenario."""
        logger.info(f"[LAE FACADE] Executing listening assessment for session '{session.session_id}'")

        if not scenario.listening_questions:
            raise ListeningModuleMissing(scenario.scenario_id)

        # 1. Initialize Listening Session & Components
        listening_session = ListeningSession(
            session_id=session.session_id,
            scenario_id=scenario.scenario_id,
            audio_id=scenario.audio_asset.url,
            questions=scenario.listening_questions,
        )

        navigator = ListeningNavigator(scenario.listening_questions)
        self.player.load_audio(scenario.audio_asset)

        await self.publisher.publish_started(session.session_id, len(scenario.listening_questions))
        self.player.start()
        await self.publisher.publish_audio_started(session.session_id, scenario.audio_asset.url, scenario.audio_asset.duration_seconds)

        # 2. Iterate through Listening Questions
        candidate_responses_by_q = {
            r.prompt_id: r for r in session.responses if isinstance(r, ListeningResponse)
        }
        is_simulation = len(candidate_responses_by_q) == 0

        for idx, q in enumerate(scenario.listening_questions):
            await self.publisher.publish_question_presented(session.session_id, q.question_id, idx, len(scenario.listening_questions))

            if q.question_id in candidate_responses_by_q:
                cand_resp = candidate_responses_by_q[q.question_id]
                listening_session.responses[q.question_id] = cand_resp
                is_correct = self.validator.is_answer_correct(q, cand_resp)
                await self.publisher.publish_answer_submitted(
                    session.session_id, q.question_id, cand_resp.selected_option_index, is_correct, cand_resp.response_time_ms or 2500
                )
            elif is_simulation:
                # Automated standalone execution simulation
                selected_option = q.correct_option_index
                response_time_ms = 2500
                response = self.collector.collect_response(
                    session_id=session.session_id,
                    question=q,
                    selected_option_index=selected_option,
                    response_time_ms=response_time_ms,
                )
                listening_session.responses[q.question_id] = response
                session.add_response(response)

                is_correct = self.validator.is_answer_correct(q, response)
                await self.publisher.publish_answer_submitted(
                    session.session_id, q.question_id, selected_option, is_correct, response_time_ms
                )

        # 3. Validate Completion & Build Result
        self.validator.validate_completion(scenario.listening_questions, listening_session.responses)

        result: ListeningSessionResult = self.result_builder.build_result(
            session_id=session.session_id,
            scenario_id=scenario.scenario_id,
            questions=scenario.listening_questions,
            responses=listening_session.responses,
            replay_status=listening_session.replay_status,
        )

        await self.publisher.publish_completed(session.session_id, result.total_questions, result.correct_count)

        logger.info(f"[LAE FACADE] Completed listening assessment for session '{session.session_id}'. Accuracy: {result.raw_accuracy_percentage}%")

        return {
            "session_id": session.session_id,
            "scenario_id": scenario.scenario_id,
            "total_questions": result.total_questions,
            "correct_count": result.correct_count,
            "raw_accuracy_percentage": result.raw_accuracy_percentage,
            "average_response_time_ms": result.average_response_time_ms,
            "responses": result.responses,
        }
