"""
Module 3.8: Interview Controller (AIIS v20.1 Architecture).
Evaluates InterviewReadinessScore (multi-signal: decision confidence, scenario understanding, language quality, intent stability)
and generates an explicit InterviewPolicy to govern downstream modules.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from app.application.followup_subsystem.intent_understanding_engine import IntentResult, CandidateIntent


class InterviewMode(str, Enum):
    GUIDANCE_MODE = "GUIDANCE_MODE"       # Candidate misunderstood or asked for help
    CLARIFY_MODE = "CLARIFY_MODE"         # Decision confidence < 0.40 or ambiguous answer
    PROBE_MODE = "PROBE_MODE"             # Readiness HIGH -> Explore missing dimensions
    VERIFY_MODE = "VERIFY_MODE"           # Position shift or contradiction detected
    REFLECTION_MODE = "REFLECTION_MODE"   # High coverage -> Deep self-reflection
    WRAP_UP_MODE = "WRAP_UP_MODE"         # Low uncertainty -> Conclude interview


class CandidateReadiness(str, Enum):
    LOW = "LOW"         # Readiness score < 0.40 -> Simplest questions, guidance
    MEDIUM = "MEDIUM"   # Readiness score 0.40-0.74 -> Standard reasoning questions
    HIGH = "HIGH"       # Readiness score >= 0.75 -> Deep probing & challenges


class QuestionDifficulty(str, Enum):
    LEVEL_1_CLARIFICATION = "LEVEL_1_CLARIFICATION" # Simple step clarification
    LEVEL_2_DECISION = "LEVEL_2_DECISION"           # Initial action inquiry
    LEVEL_3_REASONING = "LEVEL_3_REASONING"         # Rationale & stakeholder thinking
    LEVEL_4_CHALLENGE = "LEVEL_4_CHALLENGE"         # Operational pressure / trade-off challenge
    LEVEL_5_COUNTERFACTUAL = "LEVEL_5_COUNTERFACTUAL" # Complex alternative scenario switch


@dataclass
class InterviewPolicy:
    mode: InterviewMode
    readiness: CandidateReadiness
    difficulty: QuestionDifficulty
    readiness_score: float             # 0.0 to 1.0
    temperature: float                 # LLM generation temperature (0.1 to 0.7)
    allowed_objectives: List[str]
    forbidden_objectives: List[str]
    maximum_questions: int
    allow_counterfactual: bool
    allow_challenge: bool
    need_clarification: bool

    def to_dict(self) -> Dict[str, Any]:
        return {
            "mode": self.mode.value,
            "readiness": self.readiness.value,
            "difficulty": self.difficulty.value,
            "readiness_score": round(self.readiness_score, 2),
            "temperature": self.temperature,
            "allowed_objectives": self.allowed_objectives,
            "forbidden_objectives": self.forbidden_objectives,
            "maximum_questions": self.maximum_questions,
            "allow_counterfactual": self.allow_counterfactual,
            "allow_challenge": self.allow_challenge,
            "need_clarification": self.need_clarification,
        }


class InterviewController:
    """Module 3.8: Brain of the interviewer generating explicit InterviewPolicy."""

    def evaluate_policy(
        self,
        intent_res: IntentResult,
        overall_uncertainty: float,
        turn_number: int,
        contradiction_detected: bool = False,
    ) -> InterviewPolicy:

        # 1. Calculate Multi-Signal Interview Readiness Score (0.0 to 1.0)
        # 0.40 * dec_conf + 0.30 * scen_score + 0.15 * lang_score + 0.15 * (1 - repair_penalty)
        repair_penalty = 0.50 if intent_res.repair_needed else 0.0
        readiness_score = (
            0.40 * intent_res.decision_confidence
            + 0.30 * intent_res.scenario_understanding_score
            + 0.15 * intent_res.language_quality_score
            + 0.15 * (1.0 - repair_penalty)
        )
        readiness_score = round(max(min(readiness_score, 1.0), 0.0), 2)

        # 2. Determine CandidateReadiness
        if readiness_score >= 0.75:
            readiness = CandidateReadiness.HIGH
        elif readiness_score >= 0.40:
            readiness = CandidateReadiness.MEDIUM
        else:
            readiness = CandidateReadiness.LOW

        # 3. Determine InterviewMode & QuestionDifficulty
        if overall_uncertainty < 0.10:
            mode = InterviewMode.WRAP_UP_MODE
            diff = QuestionDifficulty.LEVEL_1_CLARIFICATION
            allowed = ["CONFIRM_BELIEF"]
            forbidden = ["ASK_RISK", "ASK_ALTERNATIVE", "ASK_TRADEOFF"]
            allow_count = False
            allow_chal = False
            need_clar = False
            temp = 0.2
        elif contradiction_detected:
            mode = InterviewMode.VERIFY_MODE
            diff = QuestionDifficulty.LEVEL_4_CHALLENGE
            allowed = ["VERIFY_CONSISTENCY", "VERIFY_CONTEXT"]
            forbidden = ["ASK_REFLECTION"]
            allow_count = True
            allow_chal = True
            need_clar = False
            temp = 0.3
        elif intent_res.candidate_intent in (CandidateIntent.ASKING_FOR_HELP, CandidateIntent.MISUNDERSTANDING):
            mode = InterviewMode.GUIDANCE_MODE
            diff = QuestionDifficulty.LEVEL_1_CLARIFICATION
            allowed = ["ASK_REASON"]
            forbidden = ["ASK_RISK", "ASK_TRADEOFF", "ASK_ALTERNATIVE"]
            allow_count = False
            allow_chal = False
            need_clar = True
            temp = 0.2
        elif readiness == CandidateReadiness.LOW or intent_res.needs_clarification:
            mode = InterviewMode.CLARIFY_MODE
            diff = QuestionDifficulty.LEVEL_1_CLARIFICATION if readiness_score < 0.25 else QuestionDifficulty.LEVEL_2_DECISION
            allowed = ["ASK_REASON", "CONFIRM_BELIEF"]
            forbidden = ["ASK_TRADEOFF", "ASK_ALTERNATIVE"]
            allow_count = False
            allow_chal = False
            need_clar = True
            temp = 0.3
        elif readiness == CandidateReadiness.HIGH:
            mode = InterviewMode.PROBE_MODE
            diff = QuestionDifficulty.LEVEL_4_CHALLENGE if turn_number >= 3 else QuestionDifficulty.LEVEL_3_REASONING
            allowed = ["ASK_REASON", "ASK_RISK", "ASK_STAKEHOLDER", "ASK_ALTERNATIVE", "ASK_TRADEOFF", "ASK_REFLECTION", "CONFIRM_BELIEF"]
            forbidden = []
            allow_count = turn_number >= 3
            allow_chal = True
            need_clar = False
            temp = 0.4
        else:
            mode = InterviewMode.PROBE_MODE
            diff = QuestionDifficulty.LEVEL_3_REASONING
            allowed = ["ASK_REASON", "ASK_RISK", "ASK_STAKEHOLDER", "ASK_ALTERNATIVE", "ASK_REFLECTION", "CONFIRM_BELIEF"]
            forbidden = ["ASK_TRADEOFF"]
            allow_count = False
            allow_chal = False
            need_clar = False
            temp = 0.3

        return InterviewPolicy(
            mode=mode,
            readiness=readiness,
            difficulty=diff,
            readiness_score=readiness_score,
            temperature=temp,
            allowed_objectives=allowed,
            forbidden_objectives=forbidden,
            maximum_questions=6,
            allow_counterfactual=allow_count,
            allow_challenge=allow_chal,
            need_clarification=need_clar,
        )
