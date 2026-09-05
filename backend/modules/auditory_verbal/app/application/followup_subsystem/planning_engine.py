"""
Module 7: Follow-up Planning Engine (AIIS v15.0.0).
Converts selected InterviewObjective, Candidate Decision, and Prioritized Needs into an immutable InterviewPlan.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from app.application.followup_subsystem.strategy_engine import InterviewObjective
from app.application.followup_subsystem.interview_understanding import CandidateDecisionData
from app.application.followup_subsystem.conversation_manager import ConversationState


@dataclass(frozen=True)
class InterviewPlan:
    active_objective: str
    target_dimension: str
    candidate_action: str
    scenario_context: str
    reasoning_depth: str
    reference_snippet: str
    strategic_intent: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "active_objective": self.active_objective,
            "target_dimension": self.target_dimension,
            "candidate_action": self.candidate_action,
            "scenario_context": self.scenario_context,
            "reasoning_depth": self.reasoning_depth,
            "reference_snippet": self.reference_snippet,
            "strategic_intent": self.strategic_intent,
            "metadata": self.metadata,
        }


class FollowUpPlanningEngine:
    """Module 7: Converts active InterviewObjective and candidate decision facts into deterministic InterviewPlan."""

    def create_plan(
        self,
        active_objective: InterviewObjective,
        decision_data: CandidateDecisionData,
        scenario_title: str,
        transcript_text: str,
        state: ConversationState,
    ) -> InterviewPlan:

        clean_text = (transcript_text or "").strip()
        ref_quote = decision_data.action or clean_text[:100]

        dim_map = {
            InterviewObjective.ASK_REASON: "Reason",
            InterviewObjective.ASK_RISK: "Risk",
            InterviewObjective.ASK_STAKEHOLDER: "Stakeholders",
            InterviewObjective.ASK_ALTERNATIVE: "Alternatives",
            InterviewObjective.ASK_TRADEOFF: "Tradeoffs",
            InterviewObjective.ASK_REFLECTION: "Reflection",
            InterviewObjective.VERIFY_CONSISTENCY: "Consistency",
            InterviewObjective.TEST_ADAPTABILITY: "Adaptability",
        }

        target_dim = dim_map.get(active_objective, "Reason")

        return InterviewPlan(
            active_objective=active_objective.value,
            target_dimension=target_dim,
            candidate_action=decision_data.action or "Stated response",
            scenario_context=scenario_title,
            reasoning_depth=state.edapaf_stage,
            reference_snippet=ref_quote,
            strategic_intent=f"Strategically explore dimension '{target_dim}' for candidate action '{ref_quote[:50]}'",
            metadata={"turn": state.turn_number, "stage": state.edapaf_stage},
        )
