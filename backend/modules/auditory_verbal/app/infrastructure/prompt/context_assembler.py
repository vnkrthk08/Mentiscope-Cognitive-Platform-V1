from typing import Dict, Any
from app.infrastructure.persistence.database.unit_of_work import UnitOfWork


class ContextAssembler:
    """Assembles structured deterministic context variables referencing database entities."""

    @staticmethod
    async def assemble_context(transcript_id: str) -> Dict[str, Any]:
        async with UnitOfWork() as uow:
            # Load Speech-to-Text transcript
            transcript = await uow.speech_transcripts.get_by_id(transcript_id)
            if not transcript:
                raise ValueError(f"Transcript '{transcript_id}' not found.")

            # Load scenario text (with fallbacks if scenario/assessment not found)
            scenario_text = "Standard auditory situational decision scenario task description."
            try:
                scen = await uow.scenarios.get_by_id(transcript.assessment_id)
                if scen:
                    scenario_text = scen.description
            except Exception:
                pass

            return {
                "candidate_id": transcript.candidate_id,
                "assessment_id": transcript.assessment_id,
                "scenario_text": scenario_text,
                "transcript_text": transcript.transcript_text,
            }
