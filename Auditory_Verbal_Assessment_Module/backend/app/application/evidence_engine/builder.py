from typing import Dict, Any, List
from app.infrastructure.prompt_service import PromptOrchestrationResult
from app.application.evidence_engine.models import (
    BehavioralEvidenceSet,
    BehavioralEvidence,
    BehavioralQuote,
    BehavioralIndicator,
)


class BehavioralEvidenceBuilder:
    """Transforms validated APOS output payloads into immutable BehavioralEvidenceSet domain aggregates."""

    def build_evidence_set(
        self,
        session_id: str,
        scenario_id: str,
        prompt_id: str,
        apos_result: PromptOrchestrationResult,
    ) -> BehavioralEvidenceSet:
        payload = apos_result.validated_response
        quotes_raw = payload.get("verbatim_quotes", [])
        indicators_raw = payload.get("behavioral_indicators", [])
        confidence = float(payload.get("confidence_score", 0.95))

        evidence_items: List[BehavioralEvidence] = []
        for idx, q_text in enumerate(quotes_raw):
            quote = BehavioralQuote(quote=q_text, segment_id=idx, start_time=0.0, end_time=10.0)
            indicator_text = indicators_raw[idx] if idx < len(indicators_raw) else "Observed behavioral indicator"

            item = BehavioralEvidence(
                construct=apos_result.variables_used.get("construct_name", "COMMUNICATION"),
                behavior=indicator_text,
                observation=f"Candidate demonstrated key behavior: '{indicator_text}'",
                supporting_quote=quote,
                confidence=confidence,
                source_prompt_version=apos_result.prompt_version,
                model_version=apos_result.selected_model,
            )
            evidence_items.append(item)

        indicators: List[BehavioralIndicator] = [
            BehavioralIndicator(
                name=ind,
                value="PRESENT",
                supporting_evidence_ids=[item.evidence_id for item in evidence_items],
                confidence=confidence,
            )
            for ind in indicators_raw
        ]

        return BehavioralEvidenceSet(
            session_id=session_id,
            scenario_id=scenario_id,
            prompt_id=prompt_id,
            transcript_version="1.0.0",
            evidence_version="1.0.0",
            evidence_items=evidence_items,
            indicators=indicators,
            extraction_metadata={
                "provider": apos_result.selected_provider,
                "model": apos_result.selected_model,
                "latency_ms": apos_result.latency_ms,
                "rendered_hash": apos_result.rendered_hash,
            },
        )
