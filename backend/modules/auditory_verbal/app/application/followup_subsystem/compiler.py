"""
Module 7: FollowUpSpecification Compiler (AIIS v15.0.0).
Compiles ConversationState + InterviewPlan + Candidate Decision + Memory into an immutable FollowUpSpecification.
"""

from typing import Dict, Any, Optional
from app.application.followup_subsystem.conversation_manager import ConversationState
from app.application.followup_subsystem.planning_engine import InterviewPlan
from app.application.followup_subsystem.specification import FollowUpSpecification
from app.application.followup_subsystem.style_engine import StyleProfile


class FollowUpSpecificationCompiler:
    """Compiles internal strategy states, candidate decision, style configuration, and memory into FollowUpSpecification."""

    def compile(
        self,
        state: ConversationState,
        plan: InterviewPlan,
        style_profile: StyleProfile,
        memory_reference: str = "",
    ) -> FollowUpSpecification:

        reason = f"Exploring missing dimension '{plan.target_dimension}' for objective '{plan.active_objective}' at turn {state.turn_number}."

        return FollowUpSpecification(
            intent=plan.active_objective,
            target_construct=plan.target_dimension,
            reason=reason,
            context_snippet=plan.reference_snippet,
            cognitive_depth=plan.reasoning_depth,
            conversation_stage=state.edapaf_stage,
            turn_number=state.turn_number,
            style_profile=style_profile.to_dict(),
            interviewer_memory_reference=memory_reference or f"Earlier you mentioned '{plan.reference_snippet[:50]}'.",
            questioning_style=style_profile.questioning_style,
            tone=style_profile.interviewer_tone,
            pressure_level=style_profile.pressure_level,
            empathy_level=style_profile.empathy_level,
            remaining_constructs=state.remaining_objectives,
            saturation_scores={},
            closure_probability=0.0,
            estimated_remaining_turns=len(state.remaining_objectives),
            metadata={
                "candidate_action": plan.candidate_action,
                "scenario_context": plan.scenario_context,
                "target_dimension": plan.target_dimension,
            },
        )
