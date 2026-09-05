from typing import List, Dict, Any, Optional
from app.application.scoring_engine.models import AssessmentDecision, CompositeScore


class DecisionEngine:
    """Generates deterministic assessment competency decisions and candidate reports.
    Uses strictly approved performance language ('demonstrated ability on simulated tasks')
    with zero claims regarding permanent personality or innate intelligence.
    """

    PSYCHOMETRIC_HIERARCHY_STRENGTH = ["DECISION_MAKING", "REASONING", "ADAPTABILITY", "COMMUNICATION"]
    PSYCHOMETRIC_HIERARCHY_GROWTH = ["ADAPTABILITY", "DECISION_MAKING", "REASONING", "COMMUNICATION"]

    CONSTRUCT_TITLES: Dict[str, str] = {
        "DECISION_MAKING": "Simulated Decision-Making & Planning",
        "ADAPTABILITY": "Adaptive Crisis Response & Pivoting",
        "REASONING": "Reflective Analysis & Metacognition",
        "COMMUNICATION": "Clarity, Structure & Delivery",
    }

    STRENGTH_TEMPLATES: Dict[str, str] = {
        "DECISION_MAKING": "Your strongest demonstrated ability was Decision Making ({score}/100). You decisively declared clear choices, substantiated actions with situational constraints, and outlined practical operational plans.",
        "ADAPTABILITY": "Your strongest demonstrated ability was Adaptability ({score}/100). You recognized emerging complications swiftly, effectively prioritized critical constraints, and formulated viable revised actions.",
        "REASONING": "Your strongest demonstrated ability was Reasoning ({score}/100). You insightfully evaluated trade-offs, interrogated underlying premises, and distilled actionable, transferable principles from simulated experience.",
        "COMMUNICATION": "Your strongest demonstrated ability was Communication ({score}/100). You delivered structured, articulate, and sequentially coherent explanations throughout all stages.",
    }

    GROWTH_TEMPLATES: Dict[str, str] = {
        "DECISION_MAKING": "Your primary opportunity for growth is Decision Making ({score}/100). In future simulations, focus on establishing clearer immediate commitment to a specific strategy and detailing step-by-step execution feasibility.",
        "ADAPTABILITY": "Your primary opportunity for growth is Adaptability ({score}/100). When unexpected complications arise, practice rapidly pivoting away from invalidated assumptions and isolating the primary operational bottleneck.",
        "REASONING": "Your primary opportunity for growth is Reasoning ({score}/100). Focus on deeper retrospective examination of competing trade-offs, potential vulnerabilities, and long-term ripple effects.",
        "COMMUNICATION": "Your primary opportunity for growth is Communication ({score}/100). Work on enhancing verbal delivery structure, reducing hesitation markers, and organizing points with clear causal connectives.",
    }

    def resolve_performance_band(self, score: float) -> str:
        if score >= 85.0:
            return "EXEMPLARY"
        elif score >= 70.0:
            return "PROFICIENT"
        elif score >= 55.0:
            return "DEVELOPING"
        else:
            return "EMERGING"

    def generate_decision(self, composite: CompositeScore) -> AssessmentDecision:
        score = composite.score
        risk_flags: List[str] = []

        if score >= 80.0:
            band = "HIGH_COMPETENCY"
            exp = "Candidate demonstrated exceptional problem solving, risk assessment, and clear communication under pressure."
        elif score >= 60.0:
            band = "MODERATE_COMPETENCY"
            exp = "Candidate demonstrated adequate competency across scenario objectives with minor areas for development."
        else:
            band = "DEVELOPMENT_REQUIRED"
            exp = "Candidate performance indicates key areas requiring structured developmental support."
            risk_flags.append("BELOW_BENCHMARK_SCORE")

        return AssessmentDecision(
            decision_band=band,
            decision_explanation=exp,
            risk_flags=risk_flags,
            decision_metadata={"composite_score": score, "band": band},
        )


    def generate_candidate_report(
        self,
        construct_scores: Dict[str, float],
        final_speaking_score: float,
        question_results: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Generates 100% deterministic candidate-facing assessment report without LLM dependencies."""
        overall_band = self.resolve_performance_band(final_speaking_score)

        # 1. Resolve Top Strength with Deterministic Tie-Breaking
        max_score = max(construct_scores.values()) if construct_scores else 0.0
        top_candidates = [c for c, s in construct_scores.items() if s == max_score]
        top_construct = sorted(
            top_candidates,
            key=lambda c: self.PSYCHOMETRIC_HIERARCHY_STRENGTH.index(c) if c in self.PSYCHOMETRIC_HIERARCHY_STRENGTH else 99,
        )[0] if top_candidates else "DECISION_MAKING"

        # 2. Resolve Primary Growth Area with Deterministic Tie-Breaking
        min_score = min(construct_scores.values()) if construct_scores else 0.0
        growth_candidates = [c for c, s in construct_scores.items() if s == min_score]
        growth_construct = sorted(
            growth_candidates,
            key=lambda c: self.PSYCHOMETRIC_HIERARCHY_GROWTH.index(c) if c in self.PSYCHOMETRIC_HIERARCHY_GROWTH else 99,
        )[0] if growth_candidates else "ADAPTABILITY"

        # Construct Profiles
        construct_profile = {
            c_name: {
                "title": self.CONSTRUCT_TITLES.get(c_name, c_name),
                "score": round(score, 1),
                "band": self.resolve_performance_band(score),
            }
            for c_name, score in construct_scores.items()
        }

        strength_text = self.STRENGTH_TEMPLATES.get(
            top_construct, "Demonstrated solid capabilities in simulated tasks."
        ).format(score=round(construct_scores.get(top_construct, 0.0), 1))

        growth_text = self.GROWTH_TEMPLATES.get(
            growth_construct, "Focus on continuous skill development in complex scenarios."
        ).format(score=round(construct_scores.get(growth_construct, 0.0), 1))

        return {
            "audience": "Candidate",
            "overall_speaking_score": round(final_speaking_score, 1),
            "performance_band": overall_band,
            "demonstrated_construct_scores": construct_profile,
            "key_strength": strength_text,
            "primary_growth_area": growth_text,
            "question_breakdown": question_results or [],
            "report_disclaimer": "Scores reflect observable behavioral performance demonstrated during this assessment against standardized competency indicators, and do not constitute permanent psychological or personality traits.",
            "generation_mode": "DETERMINISTIC_TIER_1_SAFE",
        }

