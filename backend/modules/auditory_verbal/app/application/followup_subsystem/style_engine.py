"""
Module: Conversation Style Engine.
Deterministically computes HOW the interviewer communicates (Tone, Questioning Style, Empathy, Pressure, Pacing).
Does NOT alter assessment strategy, psychometrics, or construct targets.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from app.application.followup_subsystem.conversation_state import ConversationState


class InterviewerTone(str, Enum):
    SUPPORTIVE = "SUPPORTIVE"
    NEUTRAL = "NEUTRAL"
    PROFESSIONAL = "PROFESSIONAL"
    CURIOUS = "CURIOUS"
    REFLECTIVE = "REFLECTIVE"
    SOCRATIC = "SOCRATIC"
    ANALYTICAL = "ANALYTICAL"
    CHALLENGING = "CHALLENGING"
    ENCOURAGING = "ENCOURAGING"
    CALM = "CALM"


class QuestioningStyle(str, Enum):
    OPEN_EXPLORATION = "OPEN_EXPLORATION"
    GUIDED_REFLECTION = "GUIDED_REFLECTION"
    HYPOTHETICAL = "HYPOTHETICAL"
    COUNTERFACTUAL = "COUNTERFACTUAL"
    EVIDENCE_PROBE = "EVIDENCE_PROBE"
    CLARIFICATION = "CLARIFICATION"
    TRADEOFF_CHALLENGE = "TRADEOFF_CHALLENGE"
    STAKEHOLDER_PERSPECTIVE = "STAKEHOLDER_PERSPECTIVE"
    ROOT_CAUSE_ANALYSIS = "ROOT_CAUSE_ANALYSIS"
    FUTURE_PROJECTION = "FUTURE_PROJECTION"


@dataclass(frozen=True)
class StyleProfile:
    interviewer_tone: str           # InterviewerTone value
    empathy_level: str              # LOW, MODERATE, HIGH
    assertiveness_level: str        # LOW, MODERATE, HIGH
    questioning_style: str          # QuestioningStyle value
    pacing: str                     # MEASURED, STANDARD, BRISK
    encouragement_level: str        # MINIMAL, MODERATE, HIGH
    pressure_level: str             # LOW, MODERATE, HIGH
    followup_length: str            # CONCISE, DETAILED, REFLECTIVE
    conversational_personality: str # EMPATHETIC_MENTOR, ANALYTICAL_EVALUATOR, SOCRATIC_GUIDE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "interviewer_tone": self.interviewer_tone,
            "empathy_level": self.empathy_level,
            "assertiveness_level": self.assertiveness_level,
            "questioning_style": self.questioning_style,
            "pacing": self.pacing,
            "encouragement_level": self.encouragement_level,
            "pressure_level": self.pressure_level,
            "followup_length": self.followup_length,
            "conversational_personality": self.conversational_personality,
        }


class ConversationStyleEngine:
    """Deterministically maps ConversationState and Interview Objective to a StyleProfile."""

    def determine_style(
        self,
        state: ConversationState,
        active_objective: str,
        transcript_text: str,
    ) -> StyleProfile:

        clean_text = (transcript_text or "").strip()
        words = len(clean_text.split())
        lowered = clean_text.lower()

        # Rule 1: Candidate Hesitation or Brief Response -> Supportive & Guided Reflection
        if words < 5 or any(h in lowered for h in ["don't know", "not sure", "dunno", "hard to say"]):
            return StyleProfile(
                interviewer_tone=InterviewerTone.SUPPORTIVE.value,
                empathy_level="HIGH",
                assertiveness_level="LOW",
                questioning_style=QuestioningStyle.CLARIFICATION.value,
                pacing="MEASURED",
                encouragement_level="HIGH",
                pressure_level="LOW",
                followup_length="CONCISE",
                conversational_personality="EMPATHETIC_MENTOR",
            )

        # Rule 2: Objective-Specific Style Alignments
        if active_objective == "EXPLORE_STAKEHOLDER_THINKING":
            return StyleProfile(
                interviewer_tone=InterviewerTone.CURIOUS.value,
                empathy_level="HIGH",
                assertiveness_level="MODERATE",
                questioning_style=QuestioningStyle.STAKEHOLDER_PERSPECTIVE.value,
                pacing="STANDARD",
                encouragement_level="MODERATE",
                pressure_level="MODERATE",
                followup_length="DETAILED",
                conversational_personality="SOCRATIC_GUIDE",
            )

        if active_objective == "COUNTERFACTUAL_REASONING":
            return StyleProfile(
                interviewer_tone=InterviewerTone.SOCRATIC.value,
                empathy_level="MODERATE",
                assertiveness_level="HIGH",
                questioning_style=QuestioningStyle.COUNTERFACTUAL.value,
                pacing="BRISK",
                encouragement_level="MINIMAL",
                pressure_level="HIGH",
                followup_length="CONCISE",
                conversational_personality="SOCRATIC_GUIDE",
            )

        if active_objective in ["EXPLORE_TRADEOFFS", "CHALLENGE_ASSUMPTION"]:
            return StyleProfile(
                interviewer_tone=InterviewerTone.ANALYTICAL.value,
                empathy_level="MODERATE",
                assertiveness_level="HIGH",
                questioning_style=QuestioningStyle.TRADEOFF_CHALLENGE.value,
                pacing="STANDARD",
                encouragement_level="MINIMAL",
                pressure_level="MODERATE",
                followup_length="DETAILED",
                conversational_personality="ANALYTICAL_EVALUATOR",
            )

        # Rule 3: Stage & Saturation Adaptations
        edapaf_stage = getattr(state, "edapaf_stage", "ADAPTIVE_FOLLOWUP")
        if edapaf_stage == "REFLECTIVE_PROBE":
            return StyleProfile(
                interviewer_tone=InterviewerTone.REFLECTIVE.value,
                empathy_level="HIGH",
                assertiveness_level="LOW",
                questioning_style=QuestioningStyle.GUIDED_REFLECTION.value,
                pacing="MEASURED",
                encouragement_level="HIGH",
                pressure_level="LOW",
                followup_length="REFLECTIVE",
                conversational_personality="EMPATHETIC_MENTOR",
            )

        ev_sat = getattr(state, "evidence_saturation", {})
        c_level = getattr(state, "challenge_level", 0)
        if len(ev_sat) >= 2 and c_level >= 3:
            return StyleProfile(
                interviewer_tone=InterviewerTone.CHALLENGING.value,
                empathy_level="LOW",
                assertiveness_level="HIGH",
                questioning_style=QuestioningStyle.FUTURE_PROJECTION.value,
                pacing="BRISK",
                encouragement_level="MINIMAL",
                pressure_level="HIGH",
                followup_length="CONCISE",
                conversational_personality="ANALYTICAL_EVALUATOR",
            )

        # Default Neutral/Professional Persona
        return StyleProfile(
            interviewer_tone=InterviewerTone.PROFESSIONAL.value,
            empathy_level="MODERATE",
            assertiveness_level="MODERATE",
            questioning_style=QuestioningStyle.OPEN_EXPLORATION.value,
            pacing="STANDARD",
            encouragement_level="MODERATE",
            pressure_level="MODERATE",
            followup_length="DETAILED",
            conversational_personality="ANALYTICAL_EVALUATOR",
        )
