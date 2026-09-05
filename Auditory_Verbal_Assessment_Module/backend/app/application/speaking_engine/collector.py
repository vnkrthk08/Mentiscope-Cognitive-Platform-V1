from typing import Dict, Any
from app.domain.entities.candidate_response import SpeakingResponse
from app.domain.entities.speaking_prompt import SpeakingPrompt


class SpeakingResponseCollector:
    """Captures recording metadata and constructs immutable SpeakingResponse domain entities."""

    def collect_response(
        self,
        session_id: str,
        prompt: SpeakingPrompt,
        recording_meta: Dict[str, Any],
    ) -> SpeakingResponse:
        return SpeakingResponse(
            session_id=session_id,
            prompt_id=prompt.prompt_id,
            audio_file_url=recording_meta["file_url"],
            duration_seconds=float(recording_meta["duration_seconds"]),
            transcript_text=None,  # No transcription in SAE!
            acoustic_metadata=recording_meta,
        )
