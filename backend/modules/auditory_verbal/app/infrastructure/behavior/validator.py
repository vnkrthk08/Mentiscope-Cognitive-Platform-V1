from typing import List, Tuple
from app.domain.behavior.entities.behavior_observation import BehaviorObservation


class EvidenceValidator:
    """Validator class checking behavioral observations integrity before persistence."""

    @staticmethod
    def validate_observations(observations: List[BehaviorObservation]) -> Tuple[List[BehaviorObservation], List[Tuple[BehaviorObservation, str]]]:
        """Filters observations, returning (valid_observations, quarantined_observations_with_reasons)."""
        valid = []
        quarantined = []
        seen_keys = set()

        for obs in observations:
            # 1. Low confidence check
            if obs.confidence.overall < 0.3:
                quarantined.append((obs, "Low confidence overall score (< 0.3)"))
                continue

            # 2. Missing quote check
            has_empty_quote = False
            for q in obs.supporting_quotes:
                if not q.quote or not q.quote.strip():
                    has_empty_quote = True
                    break
            if has_empty_quote:
                quarantined.append((obs, "Observation contains missing or empty supporting quotes"))
                continue

            # 3. Invalid timings check
            has_invalid_timing = False
            for q in obs.supporting_quotes:
                if q.start_time < 0 or q.end_time < 0 or q.end_time < q.start_time:
                    has_invalid_timing = True
                    break
            if has_invalid_timing:
                quarantined.append((obs, "Invalid timing indices"))
                continue

            # 4. Duplicate checks (same quote text and category)
            dup_key = tuple(sorted([q.quote for q in obs.supporting_quotes])) + (obs.behavior_type,)
            if dup_key in seen_keys:
                quarantined.append((obs, "Duplicate observation detected"))
                continue
            seen_keys.add(dup_key)

            valid.append(obs)

        return valid, quarantined
