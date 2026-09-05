"""
Module 2.5: Intent Understanding Engine (AIIS v20.1 Architecture).
Pure perception engine that observes candidate communication mode without making strategy decisions.
Classifies candidate intent, decision confidence, scenario understanding score, and language quality.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


class CandidateIntent(str, Enum):
    CLEAR_DECISION = "CLEAR_DECISION"             # Candidate stated clear decision + rationale
    AMBIGUOUS_DECISION = "AMBIGUOUS_DECISION"     # Candidate stated partial decision without rationale
    NO_DECISION = "NO_DECISION"                   # "I don't know", "Yes/No", empty
    MISUNDERSTANDING = "MISUNDERSTANDING"         # Candidate misunderstood scenario mechanics
    ASKING_FOR_HELP = "ASKING_FOR_HELP"           # "What should I do?", "Help me"
    THINKING_OUT_LOUD = "THINKING_OUT_LOUD"       # Hesitant, self-correcting verbal stream
    SELF_CORRECTION = "SELF_CORRECTION"           # "Sorry, I misunderstood...", "Actually no"
    EMOTIONAL_RESPONSE = "EMOTIONAL_RESPONSE"     # Frustrated, anxious, or off-topic reaction


@dataclass(frozen=True)
class IntentResult:
    candidate_intent: CandidateIntent
    decision_confidence: float          # 0.0 to 1.0
    scenario_understanding_score: float # 0.0 to 1.0
    language_quality_score: float       # 0.0 to 1.0 (Fluency indicator without penalty)
    emotion_state: str                  # NEUTRAL, CONFIDENT, UNCERTAIN, FRUSTRATED
    repair_needed: bool
    likely_goal: str
    needs_clarification: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "candidate_intent": self.candidate_intent.value,
            "decision_confidence": round(self.decision_confidence, 2),
            "scenario_understanding_score": round(self.scenario_understanding_score, 2),
            "language_quality_score": round(self.language_quality_score, 2),
            "emotion_state": self.emotion_state,
            "repair_needed": self.repair_needed,
            "likely_goal": self.likely_goal,
            "needs_clarification": self.needs_clarification,
        }


class IntentUnderstandingEngine:
    """Module 2.5: Pure Perception Intent Understanding Engine."""

    UNCERTAIN_WORDS = ["maybe", "guess", "not sure", "don't know", "dunno", "unsure", "probably"]
    HELP_WORDS = ["what should i", "help", "how do i", "can you explain", "what question"]
    MISUNDERSTANDING_WORDS = ["thought you meant", "misunderstood", "didn't realize", "wrong scenario"]
    REPAIR_WORDS = ["sorry", "actually no", "changed my mind", "let me rephrase", "my mistake"]

    def evaluate_intent(
        self,
        transcript_text: str,
        turn_number: int,
        understanding_result: Optional[Any] = None,
    ) -> IntentResult:
        clean_text = (transcript_text or "").strip()
        lower_text = clean_text.lower()
        words = clean_text.split()
        word_count = len(words)

        # 1. Intent Classification
        if understanding_result and getattr(understanding_result, "status", None) == "NONSENSICAL":
            intent = CandidateIntent.EMOTIONAL_RESPONSE
            dec_conf = 0.10
            scen_score = 0.20
            repair = True
            goal = "Nonsensical input requiring repair"
            needs_clar = True
        elif understanding_result and getattr(understanding_result, "status", None) == "VALID":
            intent = CandidateIntent.CLEAR_DECISION
            dec_conf = 0.92
            scen_score = 0.95
            repair = False
            goal = "State clear decision, risk, or rationale"
            needs_clar = False
        elif any(w in lower_text for w in self.REPAIR_WORDS):
            intent = CandidateIntent.SELF_CORRECTION
            dec_conf = 0.50
            scen_score = 0.80
            repair = True
            goal = "Self-correct previous response"
            needs_clar = False
        elif any(phrase in lower_text for phrase in self.HELP_WORDS):
            intent = CandidateIntent.ASKING_FOR_HELP
            dec_conf = 0.10
            scen_score = 0.30
            repair = False
            goal = "Request interviewer guidance"
            needs_clar = True
        elif any(w in lower_text for w in self.MISUNDERSTANDING_WORDS):
            intent = CandidateIntent.MISUNDERSTANDING
            dec_conf = 0.20
            scen_score = 0.25
            repair = True
            goal = "Clarify scenario rules"
            needs_clar = True
        elif word_count <= 3 and any(w in lower_text for w in ["yes", "no", "maybe", "okay", "sure", "fine"]):
            intent = CandidateIntent.NO_DECISION
            dec_conf = 0.15
            scen_score = 0.50
            repair = False
            goal = "Minimal verbal acknowledgement"
            needs_clar = True
        elif any(w in lower_text for w in self.UNCERTAIN_WORDS) or "..." in lower_text:
            intent = CandidateIntent.THINKING_OUT_LOUD if word_count > 6 else CandidateIntent.AMBIGUOUS_DECISION
            dec_conf = 0.45
            scen_score = 0.70
            repair = False
            goal = "Explore options hesitantly"
            needs_clar = True
        elif word_count >= 1 and any(w in lower_text for w in [
            "because", "since", "so that", "due to", "priority", "stop", "inform", "risk",
            "fail", "failing", "damage", "danger", "safety", "overheat", "cost", "delay"
        ]):
            intent = CandidateIntent.CLEAR_DECISION
            dec_conf = 0.88 if word_count < 6 else 0.92
            scen_score = 0.95
            repair = False
            goal = "State clear decision, risk, or rationale"
            needs_clar = False
        else:
            intent = CandidateIntent.AMBIGUOUS_DECISION
            dec_conf = 0.60
            scen_score = 0.85
            repair = False
            goal = "State partial action"
            needs_clar = False

        # 2. Language Quality Score (Pure fluency metric)
        lang_score = 0.90 if word_count >= 8 else (0.60 if word_count >= 4 else 0.35)

        # 3. Emotion State
        emotion = "UNCERTAIN" if dec_conf < 0.40 else ("CONFIDENT" if dec_conf >= 0.80 else "NEUTRAL")

        return IntentResult(
            candidate_intent=intent,
            decision_confidence=dec_conf,
            scenario_understanding_score=scen_score,
            language_quality_score=lang_score,
            emotion_state=emotion,
            repair_needed=repair,
            likely_goal=goal,
            needs_clarification=needs_clar,
        )
