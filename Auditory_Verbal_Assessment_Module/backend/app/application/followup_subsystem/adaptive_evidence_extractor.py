"""
Stage 1: Evidence Extraction Engine for Adaptive Follow-up Planning Layer.
Executes an LLM call via APOSFacade to extract construct-agnostic evidence from candidate responses.
Includes strict anti-hallucination grounding filters and valid hedge pattern verification.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from app.application.followup_subsystem.session_state import EvidenceLogEntry, FollowUpSessionState
from app.infrastructure.prompt_service.facade import AIPromptOrchestrationService as APOSFacade

logger = logging.getLogger(__name__)

# Strict set of valid psychometric hedging, stance, and confidence markers
VALID_HEDGE_PATTERNS = {
    "i think", "i believe", "decided to", "i decided", "plan to", "i plan",
    "propose to", "proposed", "passionate about", "although", "prefer",
    "chose to", "i chose", "chose this", "because", "since", "maybe",
    "probably", "noted that", "prohibited", "in my view", "i feel", "i banned"
}


def filter_grounded_hedges(candidate_text: str, hedges: List[str]) -> List[str]:
    """Filters hedges/markers to ensure they are strictly grounded in candidate_text and are genuine hedging phrases."""
    if not candidate_text or not hedges:
        return []
    c_lower = candidate_text.lower()
    grounded = []
    for h in hedges:
        if not isinstance(h, str):
            continue
        h_clean = h.strip()
        if not h_clean:
            continue
        h_lower = h_clean.lower()

        # Ensure phrase is a recognized hedge pattern or contains valid stance verb
        is_valid_pattern = any(pat in h_lower for pat in VALID_HEDGE_PATTERNS)
        if not is_valid_pattern:
            continue

        if h_lower in c_lower:
            grounded.append(h_clean)
        else:
            tokens = [t for t in h_lower.split() if len(t) > 2]
            if tokens and all(t in c_lower for t in tokens):
                grounded.append(h_clean)
    return list(dict.fromkeys(grounded))


class AdaptiveEvidenceExtractor:
    """Executes Stage 1 LLM evidence extraction."""

    def __init__(self, apos_facade: Optional[APOSFacade] = None):
        self.apos = apos_facade or APOSFacade()

    async def extract_evidence(
        self,
        scenario_title: str,
        candidate_response: str,
        session_state: FollowUpSessionState,
        turn_number: int = 1,
        source: str = "initial_response",
    ) -> EvidenceLogEntry:
        """Extracts structured evidence items and appends entry to session_state.evidence_log."""
        prior_logs_str = json.dumps([e.to_dict() for e in session_state.evidence_log], indent=2) if session_state.evidence_log else "[]"
        
        extracted_data = {
            "claims": [],
            "reasoning_shown": [],
            "assumptions": [],
            "hedges_or_confidence_markers": [],
            "contradictions_with_prior_turns": [],
        }

        if candidate_response and candidate_response.strip():
            try:
                res = await self.apos.execute_prompt(
                    prompt_id="ADAPTIVE_EVIDENCE_EXTRACTION_PROMPT",
                    variables={
                        "scenario_title": scenario_title,
                        "candidate_response": candidate_response,
                        "prior_evidence_log": prior_logs_str,
                    },
                    version="1.0.0",
                )
                if res and res.validated_response:
                    extracted_data = dict(res.validated_response)
            except Exception as err:
                logger.warning(f"[ADAPTIVE EVIDENCE EXTRACTOR] LLM call failed, falling back to basic extraction: {err}")
                extracted_data["claims"] = [candidate_response.strip()]

        raw_hedges = extracted_data.get("hedges_or_confidence_markers") or extracted_data.get("hedges") or []
        grounded_hedges = filter_grounded_hedges(candidate_response, raw_hedges)

        entry = EvidenceLogEntry(
            turn=turn_number,
            source=source,
            claims=extracted_data.get("claims") or [],
            reasoning_shown=extracted_data.get("reasoning_shown") or [],
            assumptions=extracted_data.get("assumptions") or [],
            hedges=grounded_hedges,
            contradictions=extracted_data.get("contradictions_with_prior_turns") or extracted_data.get("contradictions") or [],
        )

        session_state.evidence_log.append(entry)
        return entry
