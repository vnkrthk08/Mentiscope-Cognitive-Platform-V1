from typing import Any, Dict, List, Optional
from app.core.logging import logger
from app.domain.entities.assessment_session import AssessmentSession
from app.domain.entities.evidence import Evidence
from app.domain.value_objects.confidence_level import ConfidenceLevel
from app.domain.value_objects.enums import ConstructType
from app.domain.interfaces.subsystems import IEvidenceEngine
from app.infrastructure.speech_service.transcript_builder import SpeechProcessingResult, Transcript, SpeechProcessingMetadata
from app.application.evidence_engine.analyzer import TranscriptAnalyzer
from app.application.evidence_engine.coordinator import EvidencePromptCoordinator
from app.application.evidence_engine.builder import BehavioralEvidenceBuilder
from app.application.evidence_engine.validator import EvidenceValidator
from app.application.evidence_engine.repository import EvidenceRepository
from app.application.evidence_engine.publisher import EvidenceEventPublisher
from app.application.evidence_engine.models import BehavioralEvidenceSet
from app.domain.exceptions.evidence_exceptions import BehavioralEvidenceFailure


class BehavioralEvidenceExtractionEngine(IEvidenceEngine):
    """Facade for Behavioral Evidence Extraction Engine (BEEE) implementing IEvidenceEngine.
    Extracts structured, observable behavioral evidence from SpeechProcessingResult payloads.
    Communicates with LLMs EXCLUSIVELY through AI Prompt Orchestration Service (APOS).
    DOES NOT CALCULATE SCORES OR GENERATE REPORTS!
    """

    def __init__(
        self,
        analyzer: Optional[TranscriptAnalyzer] = None,
        coordinator: Optional[EvidencePromptCoordinator] = None,
        builder: Optional[BehavioralEvidenceBuilder] = None,
        validator: Optional[EvidenceValidator] = None,
        repository: Optional[EvidenceRepository] = None,
        publisher: Optional[EvidenceEventPublisher] = None,
    ):
        self.analyzer = analyzer or TranscriptAnalyzer()
        self.coordinator = coordinator or EvidencePromptCoordinator()
        self.builder = builder or BehavioralEvidenceBuilder()
        self.validator = validator or EvidenceValidator()
        self.repository = repository or EvidenceRepository()
        self.publisher = publisher or EvidenceEventPublisher()

    async def extract_evidence(
        self,
        session: AssessmentSession,
        speech_result: SpeechProcessingResult,
        prompt_id: str = "S_P1",
        construct_name: str = "DECISION_MAKING",
    ) -> BehavioralEvidenceSet:
        """Extracts structured behavioral evidence set from speech transcription result."""
        logger.info(f"[BEEE FACADE] Extracting evidence for session '{session.session_id}', prompt '{prompt_id}'")
        await self.publisher.publish_started(session.session_id, session.scenario_id)

        try:
            # 1. Analyze Transcript & Build APOS Variables
            variables = self.analyzer.prepare_variables(
                speech_result=speech_result,
                scenario_title=session.scenario_id,
                construct_name=construct_name,
            )
            await self.publisher.publish_transcript_loaded(session.session_id, len(speech_result.transcript.full_text))

            # 2. Execute Prompt through APOS (Zero direct LLM calls!)
            await self.publisher.publish_prompt_requested(session.session_id, "EVIDENCE_EXTRACTION_PROMPT")
            apos_result = await self.coordinator.extract_evidence_via_apos(variables)

            # 3. Build Immutable BehavioralEvidenceSet Aggregate
            evidence_set = self.builder.build_evidence_set(
                session_id=session.session_id,
                scenario_id=session.scenario_id,
                prompt_id=prompt_id,
                apos_result=apos_result,
            )

            # 4. Validate & Store Evidence
            self.validator.validate_evidence_set(evidence_set)
            await self.publisher.publish_evidence_validated(session.session_id, len(evidence_set.evidence_items))

            self.repository.save_evidence_set(evidence_set)
            await self.publisher.publish_evidence_stored(session.session_id, evidence_set.evidence_set_id)

            # Register extracted evidence domain entities back into AssessmentSession
            for item in evidence_set.evidence_items:
                dom_evidence = Evidence(
                    evidence_id=item.evidence_id,
                    session_id=session.session_id,
                    prompt_id=prompt_id,
                    construct=ConstructType.DECISION_MAKING,
                    quote=item.supporting_quote.quote if item.supporting_quote else "Observed behavior",
                    indicator_description=item.behavior,
                    confidence=ConfidenceLevel(item.confidence),
                )
                session.add_evidence(dom_evidence)

            await self.publisher.publish_completed(session.session_id, len(evidence_set.evidence_items), evidence_set.evidence_items[0].confidence if evidence_set.evidence_items else 0.95)
            logger.info(f"[BEEE FACADE] Completed evidence extraction for session '{session.session_id}'. Extracted {len(evidence_set.evidence_items)} items.")

            return evidence_set

        except Exception as e:
            await self.publisher.publish_failed(session.session_id, str(e))
            logger.error(f"[BEEE FACADE] Evidence extraction failed for session '{session.session_id}': {str(e)}")
            raise BehavioralEvidenceFailure(session.session_id, str(e))

    async def process_evidence_extraction(self, session: AssessmentSession) -> List[Evidence]:
        """Implementation of IEvidenceEngine abstract interface method."""
        sp_res = SpeechProcessingResult(
            session_id=session.session_id,
            prompt_id="S_P1",
            audio_url="/storage/audio/default.webm",
            transcript=Transcript(
                full_text="Candidate provided clear oral response prioritizing safety protocols and logistics re-routing.",
                segments=[],
                word_timestamps=[],
            ),
            metadata=SpeechProcessingMetadata("MockProvider", "1.0", "mock-v1", 0.5, 0.95),
        )
        ev_set = await self.extract_evidence(session, sp_res)
        return session.extracted_evidence
