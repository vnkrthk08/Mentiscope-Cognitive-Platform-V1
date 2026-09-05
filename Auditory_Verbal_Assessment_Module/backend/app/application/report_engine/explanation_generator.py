from typing import Dict, List, Any, Tuple
from app.application.scoring_engine.models import AssessmentScoreSet


class ConstructExplanationGenerator:
    """Generates construct summaries, explains score meaning, and extracts strengths/development areas."""

    def generate_explanations(
        self, score_set: AssessmentScoreSet
    ) -> Tuple[Dict[str, Dict[str, Any]], List[str], List[str]]:
        sections: Dict[str, Dict[str, Any]] = {}
        strengths: List[str] = []
        development_areas: List[str] = []

        for c_name, c_score in score_set.construct_scores.items():
            norm_val = c_score.normalized_score
            if norm_val >= 80.0:
                qualifier = "High Competency"
                strengths.append(f"Strong proficiency in {c_name} (Score: {norm_val}/100)")
            elif norm_val >= 60.0:
                qualifier = "Moderate Competency"
            else:
                qualifier = "Developmental Support Required"
                development_areas.append(f"Development opportunity in {c_name} (Score: {norm_val}/100)")

            sections[c_name] = {
                "score": norm_val,
                "qualifier": qualifier,
                "explanation": f"{c_name} evaluated at {norm_val}/100 with weight {c_score.weight}.",
                "confidence": c_score.confidence,
            }

        return sections, strengths, development_areas
