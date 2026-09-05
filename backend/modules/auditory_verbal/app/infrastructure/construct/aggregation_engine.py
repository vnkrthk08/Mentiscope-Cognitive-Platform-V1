from typing import List, Dict, Any
from app.domain.behavior.entities.behavior_observation import BehaviorObservation
from app.domain.construct.entities.construct_profile import ConstructProfile
from app.domain.construct.value_objects.evaluation_reference import EvaluationReference
from app.domain.construct.value_objects.construct_confidence import ConstructConfidence
from app.infrastructure.construct.mapping_engine import ConstructMappingEngine
from app.infrastructure.construct.confidence_calculator import ConstructConfidenceCalculator


class EvidenceAggregator:
    """Aggregates behavior observations, resolves mapping rules, and constructs profile segments."""

    @staticmethod
    def aggregate_evidence(observations: List[BehaviorObservation]) -> List[ConstructProfile]:
        # Group observations by (framework, construct_name)
        groups: Dict[tuple, List[BehaviorObservation]] = {}
        for obs in observations:
            mappings = ConstructMappingEngine.get_mappings(obs.behavior_type)
            for fw, name, strength in mappings:
                key = (fw, name)
                if key not in groups:
                    groups[key] = []
                groups[key].append(obs)

        profiles = []
        for (fw, name), obs_list in groups.items():
            # Build list of EvaluationReferences
            references = [
                EvaluationReference(reference_id=o.observation_id, reference_type="BEHAVIOR_OBSERVATION")
                for o in obs_list
            ]

            # Calculate confidence score via calculator
            conf_vo = ConstructConfidenceCalculator.calculate(obs_list, fw)

            summary = f"Evaluation of construct '{name}' under framework '{fw}' based on {len(obs_list)} supporting observation(s)."

            profiles.append(
                ConstructProfile(
                    framework=fw,
                    construct_name=name,
                    supporting_observations=references,
                    confidence=conf_vo,
                    evaluation_summary=summary,
                )
            )

        return profiles
pre=1.0
