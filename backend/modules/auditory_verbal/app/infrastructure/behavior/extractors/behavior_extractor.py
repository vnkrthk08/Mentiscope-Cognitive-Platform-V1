import json
import uuid
from typing import List, Dict, Any
from app.domain.behavior.entities.behavior_observation import BehaviorObservation
from app.domain.behavior.value_objects.quote_reference import QuoteReference
from app.domain.behavior.value_objects.evidence_confidence import EvidenceConfidence


class BehaviorExtractor:
    """Parses structural JSON outputs from PromptResponse payload to extract behavioral observations."""

    @staticmethod
    def extract_observations(content_normalized: str) -> List[BehaviorObservation]:
        observations = []
        try:
            data = json.loads(content_normalized)
        except Exception as e:
            raise ValueError(f"Failed to parse normalized content as JSON: {str(e)}")

        behaviors = data.get("behaviors", [])
        for b in behaviors:
            category = b.get("category", "General")
            description = b.get("description", "")
            quote_text = b.get("quote", "")
            
            start_idx = int(b.get("start_word_index", 0))
            end_idx = int(b.get("end_word_index", 0))
            start_time = float(b.get("start_time", 0.0))
            end_time = float(b.get("end_time", 0.0))
            conf_val = float(b.get("confidence", 1.0))
            
            linked = b.get("linked_constructs", [category])

            # Construct QuoteReference Value Object
            quote = QuoteReference(
                quote=quote_text,
                start_word_index=start_idx,
                end_word_index=end_idx,
                start_time=start_time,
                end_time=end_time,
            )

            # Construct EvidenceConfidence Value Object
            confidence = EvidenceConfidence(
                overall=conf_val,
                supporting_score=conf_val,
                consistency_score=1.0,
            )

            # Construct BehaviorObservation Entity
            obs = BehaviorObservation(
                observation_id=str(uuid.uuid4()),
                behavior_type=category,
                description=description,
                supporting_quotes=[quote],
                confidence=confidence,
                linked_constructs=linked,
            )
            observations.append(obs)

        return observations
