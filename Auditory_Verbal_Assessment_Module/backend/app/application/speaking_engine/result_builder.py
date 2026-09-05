from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Any
from app.domain.entities.speaking_prompt import SpeakingPrompt
from app.domain.entities.candidate_response import SpeakingResponse


@dataclass
class SpeakingSessionResult:
    """Result object summarizing speaking assessment execution, recording references, and timing metadata."""

    session_id: str
    scenario_id: str
    total_prompts: int
    completed_prompts_count: int
    total_speaking_duration_seconds: float
    average_prompt_duration_seconds: float
    responses: Dict[str, Dict[str, Any]]
    completed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class SpeakingResultBuilder:
    """Builds SpeakingSessionResult summary (Does NOT generate transcripts or scores!)."""

    def build_result(
        self,
        session_id: str,
        scenario_id: str,
        prompts: List[SpeakingPrompt],
        responses: Dict[str, SpeakingResponse],
    ) -> SpeakingSessionResult:
        total_prompts = len(prompts)
        total_duration = 0.0
        response_summaries: Dict[str, Dict[str, Any]] = {}

        for p in prompts:
            resp = responses.get(p.prompt_id)
            if resp:
                total_duration += resp.duration_seconds
                response_summaries[p.prompt_id] = {
                    "prompt_title": p.title,
                    "audio_file_url": resp.audio_file_url,
                    "duration_seconds": resp.duration_seconds,
                    "target_constructs": [c.value for c in p.target_constructs],
                    "acoustic_metadata": resp.acoustic_metadata,
                }

        avg_duration = round(total_duration / float(total_prompts), 1) if total_prompts > 0 else 0.0

        return SpeakingSessionResult(
            session_id=session_id,
            scenario_id=scenario_id,
            total_prompts=total_prompts,
            completed_prompts_count=len(responses),
            total_speaking_duration_seconds=round(total_duration, 1),
            average_prompt_duration_seconds=avg_duration,
            responses=response_summaries,
        )
