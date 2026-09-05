from typing import Dict, List
from app.application.evidence_engine.models import BehavioralEvidenceSet, BehavioralEvidence
from app.application.construct_engine.models import ConstructEvidenceSummary
from app.domain.exceptions.construct_exceptions import BehavioralEvidenceMissing


class ConstructGroupingService:
    """Groups behavioral evidence items by construct and aggregates evidence context for APOS evaluation."""

    def group_evidence_by_construct(
        self, evidence_set: BehavioralEvidenceSet
    ) -> Dict[str, List[BehavioralEvidence]]:
        if not evidence_set.evidence_items:
            raise BehavioralEvidenceMissing(evidence_set.session_id)

        grouped: Dict[str, List[BehavioralEvidence]] = {}
        for item in evidence_set.evidence_items:
            c_name = item.construct.upper()
            if c_name not in grouped:
                grouped[c_name] = []
            grouped[c_name].append(item)

        return grouped

    def build_evidence_summaries(
        self, grouped_evidence: Dict[str, List[BehavioralEvidence]]
    ) -> List[ConstructEvidenceSummary]:
        summaries: List[ConstructEvidenceSummary] = []
        for c_name, items in grouped_evidence.items():
            refs = [item.evidence_id for item in items]
            obs_texts = [f"'{item.behavior}' (Quote: '{item.supporting_quote.quote if item.supporting_quote else ''}')" for item in items]
            summary = ConstructEvidenceSummary(
                construct=c_name,
                evidence_count=len(items),
                indicator_count=len(items),
                evidence_references=refs,
                observation_summary=" | ".join(obs_texts),
            )
            summaries.append(summary)
        return summaries
