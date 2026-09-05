"""
Module 7.8: Conversation Flow Engine (AIIS v20.1 Architecture).
Decides turn-by-turn dialogue flow structure (should_acknowledge, should_transition, should_challenge,
should_summarize, should_compare) using dialogue memory history.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from app.application.followup_subsystem.world_model import InterviewWorldModel
from app.application.followup_subsystem.interview_controller import InterviewPolicy


@dataclass(frozen=True)
class FlowDecision:
    should_acknowledge: bool
    should_transition: bool
    should_challenge: bool
    should_summarize: bool
    should_compare: bool
    flow_pattern: str                    # ACK_AND_QUESTION, DIRECT_QUESTION, SUMMARY_AND_PROBE, CONTRAST_CHALLENGE

    def to_dict(self) -> Dict[str, Any]:
        return {
            "should_acknowledge": self.should_acknowledge,
            "should_transition": self.should_transition,
            "should_challenge": self.should_challenge,
            "should_summarize": self.should_summarize,
            "should_compare": self.should_compare,
            "flow_pattern": self.flow_pattern,
        }


class ConversationFlowEngine:
    """Module 7.8: Conversation Flow Engine evaluating turn context and dialogue memory history."""

    def evaluate_flow(self, world_model: InterviewWorldModel, policy: InterviewPolicy) -> FlowDecision:
        turn = world_model.turn_number
        mem = world_model.dialogue_memory

        # Avoid repeating acknowledgements if performed in recent turns
        ack = not mem.already_acknowledged and policy.readiness_score > 0.50 and turn % 2 == 1
        trans = turn > 1 and not mem.already_summarized
        chal = policy.allow_challenge and turn >= 3
        summ = turn >= 4 and not mem.already_summarized
        comp = policy.allow_counterfactual and turn >= 3

        if chal:
            pattern = "CONTRAST_CHALLENGE"
        elif summ:
            pattern = "SUMMARY_AND_PROBE"
        elif ack and trans:
            pattern = "ACK_AND_QUESTION"
        else:
            pattern = "DIRECT_QUESTION"

        return FlowDecision(
            should_acknowledge=ack,
            should_transition=trans,
            should_challenge=chal,
            should_summarize=summ,
            should_compare=comp,
            flow_pattern=pattern,
        )
