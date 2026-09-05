"""
Stage 5: Follow-up Specification Compiler for Adaptive Follow-up Engine.

Compiles Stage 4's strategic FollowUpObjectiveDecision, Stage 1-3 FollowUpSessionState,
and StyleEngine's StyleProfile into an immutable, canonical 18-field FollowUpSpecification DTO.
Guarantees 100% downstream compatibility with ADAPTIVE_FOLLOWUP_PROMPT (v16.0.0),
InterviewQAEngine, and DialogueEditor.
"""

import logging
from typing import Dict, List, Any, Optional
from app.application.followup_subsystem.session_state import FollowUpSessionState, EvidenceLogEntry
from app.application.followup_subsystem.adaptive_objective_planner import FollowUpObjectiveDecision
from app.application.followup_subsystem.specification import FollowUpSpecification
from app.application.followup_subsystem.style_engine import StyleProfile

logger = logging.getLogger(__name__)

# Complete deterministic mapping table for all 12 objectives
OBJECTIVE_MAPPING_TABLE: Dict[str, Dict[str, str]] = {
    "trade_off_analysis": {
        "intent": "CHALLENGE_REASONING",
        "cognitive_depth": "TRADE_OFF_DEFENSE",
    },
    "priority_shift": {
        "intent": "CHALLENGE_PRIORITY",
        "cognitive_depth": "PRIORITY_JUSTIFICATION",
    },
    "stakeholder_perspective": {
        "intent": "EXPLORE_STAKEHOLDER",
        "cognitive_depth": "STAKEHOLDER_ALIGNMENT",
    },
    "alternative_strategy": {
        "intent": "EXPLORE_ALTERNATIVE",
        "cognitive_depth": "STRATEGY_EVALUATION",
    },
    "constraint_change": {
        "intent": "TEST_ADAPTABILITY",
        "cognitive_depth": "CONSTRAINT_ADAPTATION",
    },
    "reasoning_probe": {
        "intent": "PROBE_REASONING",
        "cognitive_depth": "REASONING_DEPTH",
    },
    "clarification": {
        "intent": "CLARIFY_AMBIGUITY",
        "cognitive_depth": "CLARIFICATION",
    },
    "ethical_challenge": {
        "intent": "CHALLENGE_ETHICS",
        "cognitive_depth": "ETHICAL_JUSTIFICATION",
    },
    "failure_recovery": {
        "intent": "PROBE_RECOVERY",
        "cognitive_depth": "FAILURE_RESILIENCE",
    },
    "risk_assessment": {
        "intent": "EVALUATE_RISK",
        "cognitive_depth": "RISK_MITIGATION",
    },
    "contradiction_detection": {
        "intent": "RESOLVE_CONTRADICTION",
        "cognitive_depth": "CONTRADICTION_RESOLUTION",
    },
    "confidence_verification": {
        "intent": "VERIFY_CONFIDENCE",
        "cognitive_depth": "CONFIDENCE_PROBE",
    },
}

# Safe fallback values if an unmapped objective is encountered
DEFAULT_FALLBACK_MAPPING = {
    "intent": "PROBE_MISSING_CONSTRUCT",
    "cognitive_depth": "CONSTRUCT_EXPLORATION",
}


class AdaptiveFollowUpSpecificationCompiler:
    """Compiles Stage 4 decisions into canonical FollowUpSpecification DTOs."""

    def compile(
        self,
        decision: FollowUpObjectiveDecision,
        session_state: FollowUpSessionState,
        style_profile: Optional[StyleProfile] = None,
        turn_number: int = 1,
        transcript_text: str = "",
        conversation_stage: str = "ADAPTIVE_FOLLOWUP",
        existing_metadata: Optional[Dict[str, Any]] = None,
    ) -> FollowUpSpecification:
        """
        Compiles FollowUpObjectiveDecision into FollowUpSpecification.

        Args:
            decision: Stage 4 FollowUpObjectiveDecision.
            session_state: Current FollowUpSessionState.
            style_profile: StyleProfile from StyleEngine.
            turn_number: Current turn number.
            transcript_text: Latest candidate response transcript text.
            conversation_stage: Current stage string.
            existing_metadata: Optional pre-existing metadata dict to merge additively.
        """
        obj_key = (decision.objective or "").strip().lower()
        mapping = OBJECTIVE_MAPPING_TABLE.get(obj_key)

        if not mapping:
            logger.warning(
                f"[SPECIFICATION COMPILER] Unmapped objective '{decision.objective}' — "
                f"applied safe fallback mapping (intent=PROBE_MISSING_CONSTRUCT, depth=CONSTRUCT_EXPLORATION)"
            )
            mapping = DEFAULT_FALLBACK_MAPPING

        # Target construct extraction with explicit fallback warning
        fallback_applied = False
        if decision.target_constructs and len(decision.target_constructs) > 0:
            target_constructs = decision.target_constructs
        else:
            fallback_c = session_state.primary_constructs[0] if session_state.primary_constructs else "DECISION_MAKING"
            logger.warning(
                f"[SPECIFICATION COMPILER] Empty target_constructs list in decision for objective '{decision.objective}' — "
                f"falling back to primary construct '{fallback_c}' from scenario declaration."
            )
            target_constructs = [fallback_c]
            fallback_applied = True

        primary_target_construct = target_constructs[0]
        is_dual_target = len(target_constructs) > 1

        # Extract context_snippet from Stage 1's latest evidence entry
        context_snippet = self._extract_context_snippet(session_state, transcript_text)

        # Formulate interviewer memory reference from prior turn evidence
        memory_reference = self._extract_memory_reference(session_state, context_snippet)

        # Process style_profile values consistently across dict and top-level fields
        if style_profile:
            style_dict = style_profile.to_dict()
            questioning_style = style_profile.questioning_style
            tone = style_profile.interviewer_tone
            pressure_level = style_profile.pressure_level
            empathy_level = style_profile.empathy_level
        else:
            tone = "NEUTRAL"
            pressure_level = "MODERATE"
            empathy_level = "MODERATE"
            questioning_style = "GUIDED_REFLECTION"
            style_dict = {
                "interviewer_tone": tone,
                "empathy_level": empathy_level,
                "assertiveness_level": "MODERATE",
                "questioning_style": questioning_style,
                "pacing": "STANDARD",
                "encouragement_level": "MODERATE",
                "pressure_level": pressure_level,
                "followup_length": "DETAILED",
                "conversational_personality": "ANALYTICAL_EVALUATOR",
            }

        # Calculate remaining constructs (constructs not yet sufficient)
        remaining_constructs = [
            c_name
            for c_name, cov in session_state.construct_coverage.items()
            if cov.status != "sufficient"
        ]

        # Calculate saturation scores dictionary from construct_coverage
        saturation_scores = {
            c_name: round(cov.confidence, 2)
            for c_name, cov in session_state.construct_coverage.items()
        }

        # Additive metadata merging: preserves existing metadata keys without overwriting
        metadata = dict(existing_metadata or {})
        metadata.update({
            "dual_target_constructs": target_constructs,
            "is_dual_target": is_dual_target,
            "target_construct_fallback_applied": fallback_applied,
            "constraints": decision.constraints,
            "is_repeat": decision.is_repeat,
            "stage4_reason": decision.reason,
        })

        return FollowUpSpecification(
            intent=mapping["intent"],
            target_construct=primary_target_construct,
            reason=decision.reason,
            context_snippet=context_snippet,
            cognitive_depth=mapping["cognitive_depth"],
            conversation_stage=conversation_stage,
            turn_number=turn_number,
            style_profile=style_dict,
            interviewer_memory_reference=memory_reference,
            questioning_style=questioning_style,
            tone=tone,
            pressure_level=pressure_level,
            empathy_level=empathy_level,
            remaining_constructs=remaining_constructs,
            saturation_scores=saturation_scores,
            # TODO (v20.2): Hardcoded v1 stub. Closure probability computation is deferred until InterviewClosureEngine is integrated.
            closure_probability=0.0,
            # TODO (v20.2): Naive v1 stub. Estimated remaining turns currently equals count of non-sufficient constructs.
            estimated_remaining_turns=len(remaining_constructs),
            metadata=metadata,
        )

    def _extract_context_snippet(
        self,
        session_state: FollowUpSessionState,
        transcript_text: str,
    ) -> str:
        """Extracts verbatim context snippet from Stage 1's latest evidence log entry."""
        if session_state.evidence_log:
            latest_entry = session_state.evidence_log[-1]
            if latest_entry.claims:
                return latest_entry.claims[0]

        clean_text = (transcript_text or "").strip()
        if clean_text:
            return clean_text[:120]
        return "Stated candidate response"

    def _extract_memory_reference(
        self,
        session_state: FollowUpSessionState,
        current_snippet: str,
    ) -> str:
        """Constructs a grounded memory reference referencing prior turn claims."""
        if len(session_state.evidence_log) > 1:
            prior_entry = session_state.evidence_log[-2]
            if prior_entry.claims:
                claim_sample = prior_entry.claims[0][:60]
                return f"Earlier in turn {prior_entry.turn}, you mentioned '{claim_sample}'."

        if current_snippet:
            return f"Regarding your point '{current_snippet[:60]}'."
        return "Based on your previous statement."
