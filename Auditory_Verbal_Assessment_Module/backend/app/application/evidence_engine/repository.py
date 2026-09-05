from typing import Dict, List, Optional
from app.application.evidence_engine.models import BehavioralEvidenceSet


class EvidenceRepository:
    """In-memory persistence and versioning repository for BehavioralEvidenceSet aggregates."""

    def __init__(self):
        self._records: Dict[str, List[BehavioralEvidenceSet]] = {}

    def save_evidence_set(self, evidence_set: BehavioralEvidenceSet):
        if evidence_set.session_id not in self._records:
            self._records[evidence_set.session_id] = []
        self._records[evidence_set.session_id].append(evidence_set)

    def get_latest_evidence_set(self, session_id: str) -> Optional[BehavioralEvidenceSet]:
        sets = self._records.get(session_id, [])
        return sets[-1] if sets else None
