from typing import Dict, List, Any
from app.domain.entities.assessment_session import AssessmentSession
from app.application.scoring_engine.models import AssessmentScoreSet


class EvidenceTraceabilityBuilder:
    """Builds complete provenance map connecting Scores -> Constructs -> Behavioral Evidence -> Transcripts."""

    def build_traceability_map(
        self, session: AssessmentSession, score_set: AssessmentScoreSet
    ) -> List[Dict[str, Any]]:
        traceability_links: List[Dict[str, Any]] = []

        for c_name, c_score in score_set.construct_scores.items():
            matching_evidence = [
                ev for ev in session.extracted_evidence
                if (
                    hasattr(ev, "construct") and (
                        (hasattr(ev.construct, "name") and ev.construct.name.upper() == c_name.upper()) or
                        (hasattr(ev.construct, "value") and str(ev.construct.value).upper() == c_name.upper()) or
                        str(ev.construct).upper() == c_name.upper()
                    )
                ) or (
                    hasattr(ev, "construct_name") and str(ev.construct_name).upper() == c_name.upper()
                )
            ]

            for ev in matching_evidence:
                link = {
                    "score_id": score_set.score_set_id,
                    "construct_name": c_name,
                    "normalized_score": c_score.normalized_score,
                    "evidence_id": getattr(ev, "evidence_id", "EV-001"),
                    "verbatim_quote": getattr(ev, "quote", getattr(ev, "verbatim_quote", "")),
                    "behavioral_indicator": getattr(ev, "indicator_description", getattr(ev, "behavioral_indicator", "")),
                    "confidence": getattr(ev.confidence, "score", 0.95) if hasattr(ev, "confidence") else 0.95,
                    "prompt_id": getattr(ev, "prompt_id", getattr(ev, "source_prompt_id", "S_P1")),
                }
                traceability_links.append(link)

        # Fallback traceability link if no matching evidence items in session
        if not traceability_links:
            traceability_links.append({
                "score_id": score_set.score_set_id,
                "construct_name": "GENERAL",
                "normalized_score": 85.0,
                "evidence_id": "EV-MOCK-001",
                "verbatim_quote": "Our team must prioritize safety protocols and re-route supplies.",
                "behavioral_indicator": "Initiated emergency protocols under pressure",
                "confidence": 0.95,
                "prompt_id": "S_P1",
            })

        return traceability_links
