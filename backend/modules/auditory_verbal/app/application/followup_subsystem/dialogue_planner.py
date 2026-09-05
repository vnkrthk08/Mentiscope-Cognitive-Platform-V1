"""
Module 7.5: Dialogue Planner (AIIS v20.1 Architecture).
Pure semantic planner that outputs abstract semantic DialogueActs (InterviewMoves, acknowledgement types,
transition types, uncertainty targets) WITHOUT generating English text.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from app.application.followup_subsystem.interview_controller import InterviewPolicy, InterviewMode, QuestionDifficulty


class InterviewMove(str, Enum):
    VALIDATE = "VALIDATE"                 # Validate decision & acknowledge reasoning
    CLARIFY = "CLARIFY"                   # Simple step or ambiguity clarification
    EXPLORE = "EXPLORE"                   # Explore missing dimension / risk / alternative
    CHALLENGE = "CHALLENGE"               # Present operational pressure or trade-off challenge
    HYPOTHESIS_TEST = "HYPOTHESIS_TEST"   # Test dynamic belief hypothesis
    REFLECT = "REFLECT"                   # Prompt metacognitive self-reflection
    REDIRECT = "REDIRECT"                 # Redirect off-topic / nonsensical response
    SUMMARIZE = "SUMMARIZE"               # Summarize candidate rationale & verify
    ENCOURAGE = "ENCOURAGE"               # Supportive encouragement for short responses
    REPAIR = "REPAIR"                     # Repair misunderstanding or self-correction


@dataclass(frozen=True)
class SemanticDialogueAct:
    interview_move: InterviewMove
    acknowledgement_type: str            # NONE, VALIDATE_DECISION, EMPATHIZE, REFRAME
    transition_type: str                 # DIRECT, SHIFT_TO_UNCERTAINTY, CONTRAST, SUMMARY
    reference_summary: str               # Polished single-generation semantic summary
    uncertainty_target: str              # operational_risk, decision_rationale, stakeholder_impact, alternative_options
    difficulty_level: str                # LEVEL_1 to LEVEL_5
    expected_answer_type: str            # REASONING, ACTION_STEP, TRADE_OFF_JUSTIFICATION, SELF_REFLECTION

    def to_dict(self) -> Dict[str, Any]:
        return {
            "interview_move": self.interview_move.value,
            "acknowledgement_type": self.acknowledgement_type,
            "transition_type": self.transition_type,
            "reference_summary": self.reference_summary,
            "uncertainty_target": self.uncertainty_target,
            "difficulty_level": self.difficulty_level,
            "expected_answer_type": self.expected_answer_type,
        }


class DialoguePlanner:
    """Module 7.5: Pure Semantic Dialogue Act Planner."""

    MOVE_MAP: Dict[str, InterviewMove] = {
        "ASK_REASON": InterviewMove.EXPLORE,
        "ASK_RISK": InterviewMove.EXPLORE,
        "ASK_STAKEHOLDER": InterviewMove.EXPLORE,
        "ASK_ALTERNATIVE": InterviewMove.EXPLORE,
        "ASK_TRADEOFF": InterviewMove.CHALLENGE,
        "ASK_REFLECTION": InterviewMove.REFLECT,
        "CONFIRM_BELIEF": InterviewMove.HYPOTHESIS_TEST,
        "VERIFY_CONSISTENCY": InterviewMove.CHALLENGE,
        "VERIFY_CONTEXT": InterviewMove.HYPOTHESIS_TEST,
    }

    def plan_dialogue_act(
        self,
        objective: str,
        policy: InterviewPolicy,
        candidate_summary: str,
        target_dimension: str,
    ) -> SemanticDialogueAct:

        # Select Interview Move
        if policy.mode == InterviewMode.GUIDANCE_MODE:
            move = InterviewMove.REPAIR
            ack_type = "EMPATHIZE"
            trans_type = "DIRECT"
            ans_type = "ACTION_STEP"
        elif policy.mode == InterviewMode.CLARIFY_MODE:
            move = InterviewMove.CLARIFY
            ack_type = "VALIDATE_DECISION"
            trans_type = "DIRECT"
            ans_type = "ACTION_STEP"
        elif policy.mode == InterviewMode.VERIFY_MODE:
            move = InterviewMove.CHALLENGE
            ack_type = "REFRAME"
            trans_type = "CONTRAST"
            ans_type = "TRADE_OFF_JUSTIFICATION"
        else:
            move = self.MOVE_MAP.get(objective, InterviewMove.EXPLORE)
            ack_type = "VALIDATE_DECISION" if policy.readiness_score > 0.60 else "NONE"
            trans_type = "SHIFT_TO_UNCERTAINTY"
            ans_type = "REASONING"

        target = f"{target_dimension.lower()}_uncertainty"

        return SemanticDialogueAct(
            interview_move=move,
            acknowledgement_type=ack_type,
            transition_type=trans_type,
            reference_summary=candidate_summary,
            uncertainty_target=target,
            difficulty_level=policy.difficulty.value,
            expected_answer_type=ans_type,
        )
