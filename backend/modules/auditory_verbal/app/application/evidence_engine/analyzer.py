from typing import Dict, Any
from app.infrastructure.speech_service.transcript_builder import SpeechProcessingResult
from app.domain.exceptions.evidence_exceptions import TranscriptMissing


class TranscriptAnalyzer:
    """Prepares structured prompt variables from SpeechProcessingResult payloads."""

    def prepare_variables(
        self,
        speech_result: SpeechProcessingResult,
        scenario_title: str,
        construct_name: str,
    ) -> Dict[str, Any]:
        transcript_text = speech_result.transcript.full_text
        if not transcript_text:
            raise TranscriptMissing(speech_result.session_id)

        return {
            "scenario_title": scenario_title,
            "transcript_text": transcript_text,
            "construct_name": construct_name,
        }
