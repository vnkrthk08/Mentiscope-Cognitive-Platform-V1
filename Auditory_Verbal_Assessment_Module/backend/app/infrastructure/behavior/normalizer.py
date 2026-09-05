import uuid
from datetime import datetime, timezone
from typing import List
from app.domain.behavior.entities.behavior_evidence import BehaviorEvidence
from app.domain.behavior.entities.behavior_observation import BehaviorObservation
from app.domain.behavior.entities.evidence_source import EvidenceSource
from app.domain.behavior.value_objects.evidence_metadata import EvidenceMetadata


class EvidenceNormalizer:
    """Normalizes extracted observations and provenance structures into a single unified aggregate root."""

    @staticmethod
    def normalize(
        transcript_id: str,
        execution_id: str,
        candidate_id: str,
        assessment_id: str,
        scenario_id: str,
        observations: List[BehaviorObservation],
        sources: List[EvidenceSource],
    ) -> BehaviorEvidence:
        # Calculate overall confidence as average of observations confidences
        overall_conf = 1.0
        if observations:
            overall_conf = sum(o.confidence.overall for o in observations) / len(observations)

        # Build set of all unique constructs linked
        constructs = set()
        for o in observations:
            for c in o.linked_constructs:
                constructs.add(c)

        meta = EvidenceMetadata(
            pipeline_version="1.0.0",
            model_version="gpt-5-turbo",
        )

        return BehaviorEvidence(
            evidence_id=str(uuid.uuid4()),
            transcript_id=transcript_id,
            prompt_execution_id=execution_id,
            candidate_id=candidate_id,
            assessment_id=assessment_id,
            scenario_id=scenario_id,
            construct_candidates=list(constructs),
            behavior_observations=observations,
            evidence_sources=sources,
            overall_confidence=overall_conf,
            metadata=meta,
        )
