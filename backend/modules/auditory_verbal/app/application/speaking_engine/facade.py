from typing import Any, Dict, Optional
from app.core.logging import logger
from app.domain.entities.assessment_session import AssessmentSession
from app.domain.entities.scenario import Scenario
from app.domain.interfaces.executors import ISpeakingExecutor
from app.application.speaking_engine.session import SpeakingSession
from app.application.speaking_engine.recording_manager import RecordingManager
from app.application.speaking_engine.validator import RecordingValidator
from app.application.speaking_engine.navigator import SpeakingNavigator
from app.application.speaking_engine.collector import SpeakingResponseCollector
from app.application.speaking_engine.result_builder import SpeakingResultBuilder, SpeakingSessionResult
from app.application.speaking_engine.publisher import SpeakingEventPublisher
from app.domain.exceptions.speaking_exceptions import SpeakingModuleMissing, SpeakingSessionFailure


class SpeakingAssessmentEngine(ISpeakingExecutor):
    """Facade for the Speaking Assessment Engine (SAE) implementing ISpeakingExecutor.
    Executes speaking prompt presentation, audio recording lifecycle, basic validation,
    and result building. ZERO AI / Transcription!
    """

    def __init__(
        self,
        recording_manager: Optional[RecordingManager] = None,
        validator: Optional[RecordingValidator] = None,
        collector: Optional[SpeakingResponseCollector] = None,
        result_builder: Optional[SpeakingResultBuilder] = None,
        publisher: Optional[SpeakingEventPublisher] = None,
    ):
        self.recording_manager = recording_manager or RecordingManager()
        self.validator = validator or RecordingValidator()
        self.collector = collector or SpeakingResponseCollector()
        self.result_builder = result_builder or SpeakingResultBuilder()
        self.publisher = publisher or SpeakingEventPublisher()

    async def execute(self, session: AssessmentSession, scenario: Scenario) -> Dict[str, Any]:
        """Executes complete speaking assessment recording pipeline for a scenario."""
        logger.info(f"[SAE FACADE] Executing speaking assessment for session '{session.session_id}'")

        if not scenario.speaking_prompts:
            raise SpeakingModuleMissing(scenario.scenario_id)

        # 1. Initialize Speaking Session & Components
        speaking_session = SpeakingSession(
            session_id=session.session_id,
            scenario_id=scenario.scenario_id,
            prompts=scenario.speaking_prompts,
        )

        navigator = SpeakingNavigator(scenario.speaking_prompts)
        self.recording_manager.initialize_device()
        await self.publisher.publish_started(session.session_id, len(scenario.speaking_prompts))

        # 2. Iterate through Speaking Prompts
        for idx, prompt in enumerate(scenario.speaking_prompts):
            await self.publisher.publish_prompt_presented(session.session_id, prompt.prompt_id, idx, len(scenario.speaking_prompts))

            # Simulate recording lifecycle
            self.recording_manager.start_recording(prompt.prompt_id)
            await self.publisher.publish_recording_started(session.session_id, prompt.prompt_id, float(prompt.time_limit.max_seconds))

            # Stop recording and capture metadata
            rec_meta = self.recording_manager.stop_recording(prompt.prompt_id)
            await self.publisher.publish_recording_stopped(session.session_id, prompt.prompt_id, rec_meta["duration_seconds"])

            # Validate recording file
            self.validator.validate_recording(rec_meta)

            # Collect response entity
            response = self.collector.collect_response(session.session_id, prompt, rec_meta)
            speaking_session.responses[prompt.prompt_id] = response
            session.add_response(response)

            await self.publisher.publish_response_captured(
                session.session_id, prompt.prompt_id, response.audio_file_url, response.duration_seconds, rec_meta
            )

        # 3. Build Result Summary
        result: SpeakingSessionResult = self.result_builder.build_result(
            session_id=session.session_id,
            scenario_id=scenario.scenario_id,
            prompts=scenario.speaking_prompts,
            responses=speaking_session.responses,
        )

        await self.publisher.publish_completed(session.session_id, scenario.speaking_prompts[-1].prompt_id, scenario.speaking_prompts[-1].prompt_id)

        logger.info(f"[SAE FACADE] Completed speaking assessment for session '{session.session_id}'. Total duration: {result.total_speaking_duration_seconds}s")

        return {
            "session_id": session.session_id,
            "scenario_id": scenario.scenario_id,
            "total_prompts": result.total_prompts,
            "completed_prompts_count": result.completed_prompts_count,
            "total_speaking_duration_seconds": result.total_speaking_duration_seconds,
            "average_prompt_duration_seconds": result.average_prompt_duration_seconds,
            "responses": result.responses,
        }
