import pytest
from app.application.evidence_engine import (
    BehavioralEvidenceExtractionEngine,
    TranscriptAnalyzer,
    EvidencePromptCoordinator,
    BehavioralEvidenceBuilder,
    EvidenceValidator,
    EvidenceRepository,
    BehavioralEvidenceSet,
)
from app.infrastructure.speech_service import (
    SpeechProcessingResult,
    Transcript,
    TranscriptSegment,
    WordTimestamp,
    SpeechProcessingMetadata,
)
from app.domain.entities.assessment_session import AssessmentSession
from app.domain.exceptions.evidence_exceptions import (
    TranscriptMissing,
    EvidenceValidationFailure,
    BehavioralEvidenceFailure,
)


def _create_mock_speech_result():
    return SpeechProcessingResult(
        session_id="SESS-BEEE-001",
        prompt_id="S_P1",
        audio_url="/storage/audio/rec.webm",
        transcript=Transcript(
            full_text="Our team must prioritize safety protocols immediately by re-routing medical supplies.",
            segments=[TranscriptSegment(segment_id=0, start_time=0.0, end_time=5.0, text="Our team must prioritize safety protocols.", confidence=0.96)],
            word_timestamps=[WordTimestamp(word="safety", start_time=1.0, end_time=1.5, confidence=0.98)],
        ),
        metadata=SpeechProcessingMetadata(
            provider_name="MockWhisper",
            provider_version="1.0",
            model_version="whisper-v3",
            processing_duration_seconds=0.5,
            overall_confidence=0.96,
        ),
    )


def test_transcript_analyzer():
    analyzer = TranscriptAnalyzer()
    sp_res = _create_mock_speech_result()

    vars_dict = analyzer.prepare_variables(sp_res, "Logistics Crisis", "DECISION_MAKING")
    assert vars_dict["scenario_title"] == "Logistics Crisis"
    assert "safety protocols" in vars_dict["transcript_text"]
    assert vars_dict["construct_name"] == "DECISION_MAKING"

    # Empty transcript exception
    empty_res = SpeechProcessingResult(
        session_id="SESS-EMPTY",
        prompt_id="S_P1",
        transcript=Transcript("", [], []),
    )
    with pytest.raises(TranscriptMissing):
        analyzer.prepare_variables(empty_res, "Logistics", "DECISION_MAKING")


def test_evidence_validator_and_repository():
    validator = EvidenceValidator()
    repo = EvidenceRepository()

    sp_res = _create_mock_speech_result()
    session = AssessmentSession(session_id="SESS-BEEE-001", candidate_id="CAND-01", scenario_id="SCENARIO_01")

    builder = BehavioralEvidenceBuilder()
    from app.infrastructure.prompt_service.result import PromptOrchestrationResult

    mock_apos_res = PromptOrchestrationResult(
        prompt_id="EVIDENCE_EXTRACTION_PROMPT",
        validated_response={
            "verbatim_quotes": ["prioritize safety protocols"],
            "behavioral_indicators": ["Initiated emergency protocol"],
            "confidence_score": 0.94,
        },
        variables_used={"construct_name": "DECISION_MAKING"},
    )

    ev_set = builder.build_evidence_set("SESS-BEEE-001", "SCENARIO_01", "S_P1", mock_apos_res)
    assert validator.validate_evidence_set(ev_set) is True

    repo.save_evidence_set(ev_set)
    retrieved = repo.get_latest_evidence_set("SESS-BEEE-001")
    assert retrieved.evidence_set_id == ev_set.evidence_set_id


@pytest.mark.asyncio
async def test_beee_facade_end_to_end_extraction():
    beee = BehavioralEvidenceExtractionEngine()
    session = AssessmentSession(session_id="SESS-BEEE-001", candidate_id="CAND-01", scenario_id="SCENARIO_LOGISTICS_01")
    sp_res = _create_mock_speech_result()

    ev_set = await beee.extract_evidence(session, sp_res, prompt_id="S_P1", construct_name="DECISION_MAKING")

    assert ev_set.session_id == "SESS-BEEE-001"
    assert ev_set.scenario_id == "SCENARIO_LOGISTICS_01"
    assert len(ev_set.evidence_items) > 0
    assert ev_set.evidence_items[0].construct == "DECISION_MAKING"
    assert ev_set.evidence_items[0].supporting_quote.quote != ""
    assert len(session.extracted_evidence) > 0  # Registered in session aggregate
