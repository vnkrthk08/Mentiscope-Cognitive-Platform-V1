"""
Module 6: Interview Strategy Engine (AIIS v15.0.0).
Selects EXACTLY ONE objective out of the allowed set based on Information Need Prioritization and Interviewer Action.
Allowed Objectives: ASK_REASON, ASK_RISK, ASK_STAKEHOLDER, ASK_ALTERNATIVE, ASK_TRADEOFF, ASK_REFLECTION, VERIFY_CONSISTENCY, TEST_ADAPTABILITY.
Never returns multiple objectives.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from app.application.followup_subsystem.conversation_manager import ConversationState, InterviewerAction
from app.application.followup_subsystem.decision_gap_prioritization import PrioritizedInformationNeed


class InterviewObjective(str, Enum):
    ASK_REASON = "ASK_REASON"
    ASK_RISK = "ASK_RISK"
    ASK_STAKEHOLDER = "ASK_STAKEHOLDER"
    ASK_ALTERNATIVE = "ASK_ALTERNATIVE"
    ASK_TRADEOFF = "ASK_TRADEOFF"
    ASK_REFLECTION = "ASK_REFLECTION"
    VERIFY_CONSISTENCY = "VERIFY_CONSISTENCY"
    TEST_ADAPTABILITY = "TEST_ADAPTABILITY"
    CONFIRM_BELIEF = "CONFIRM_BELIEF"
    VERIFY_CONTEXT = "VERIFY_CONTEXT"

    # Backward compatibility aliases
    CLARIFY_AMBIGUITY = "ASK_REASON"
    COLLECT_MISSING_EVIDENCE = "ASK_REASON"
    CHALLENGE_ASSUMPTION = "ASK_RISK"
    INCREASE_COGNITIVE_LOAD = "ASK_TRADEOFF"
    PROBE_LEADERSHIP = "ASK_STAKEHOLDER"
    PROBE_ETHICS = "ASK_RISK"
    EXPLORE_TRADEOFFS = "ASK_TRADEOFF"
    EXPLORE_RISK_AWARENESS = "ASK_RISK"
    EXPLORE_STAKEHOLDER_THINKING = "ASK_STAKEHOLDER"
    COUNTERFACTUAL_REASONING = "ASK_ALTERNATIVE"
    REFLECTIVE_THINKING = "ASK_REFLECTION"
    STRESS_RESPONSE = "ASK_RISK"
    DECISION_JUSTIFICATION = "ASK_REASON"


class InterviewStrategyEngine:
    """Module 6: Selects EXACTLY ONE Interview Objective based on gap priority, policy, and action."""

    def select_objective(
        self,
        action: InterviewerAction,
        prioritized_needs: List[PrioritizedInformationNeed],
        state: ConversationState,
        policy: Optional[Any] = None,
        target_construct: Optional[str] = None,
        information_gain_dimension: Optional[str] = None,
    ) -> InterviewObjective:

        already_asked = set(state.already_asked_objectives)
        allowed_set = set(policy.allowed_objectives) if (policy and getattr(policy, "allowed_objectives", None)) else None
        forbidden_set = set(policy.forbidden_objectives) if (policy and getattr(policy, "forbidden_objectives", None)) else set()

        # Helper to pick top unasked objective from prioritized needs
        def get_top_unasked_need(filter_allowed: bool = True) -> Optional[InterviewObjective]:
            for need in prioritized_needs:
                if need.objective not in already_asked and need.objective not in forbidden_set:
                    if not filter_allowed or allowed_set is None or need.objective in allowed_set:
                        try:
                            return InterviewObjective(need.objective)
                        except ValueError:
                            pass
            return None

        # 1. Action-driven overrides
        if action == InterviewerAction.VERIFY_CONSISTENCY:
            return InterviewObjective.VERIFY_CONSISTENCY

        if action in (InterviewerAction.CLARIFY, InterviewerAction.ELABORATE, InterviewerAction.REALISTIC_ANSWER, InterviewerAction.REDUCE_DIFFICULTY):
            if "ASK_REASON" not in already_asked and "ASK_REASON" not in forbidden_set:
                return InterviewObjective.ASK_REASON
            unasked = get_top_unasked_need()
            if unasked:
                return unasked

        if action == InterviewerAction.SWITCH_OBJECTIVE:
            unasked = get_top_unasked_need()
            return unasked if unasked else InterviewObjective.TEST_ADAPTABILITY

        # 2. Priority-driven objective selection (Module 5 ranking filtered by policy)
        top_obj = get_top_unasked_need(filter_allowed=True)
        if top_obj:
            return top_obj

        # Fallback without strict allowed set filter
        top_obj_any = get_top_unasked_need(filter_allowed=False)
        if top_obj_any:
            return top_obj_any

        # 3. Default Fallback across diverse core objectives if all prioritized needs asked
        core_pool = [
            InterviewObjective.ASK_RISK,
            InterviewObjective.ASK_ALTERNATIVE,
            InterviewObjective.ASK_STAKEHOLDER,
            InterviewObjective.ASK_TRADEOFF,
            InterviewObjective.ASK_REFLECTION,
            InterviewObjective.ASK_REASON,
        ]
        for obj in core_pool:
            if obj.value not in already_asked and obj.value not in forbidden_set:
                return obj

        # If everything in pool asked, rotate based on turn number
        turn_idx = (state.turn_number - 1) % len(core_pool)
        return core_pool[turn_idx]
