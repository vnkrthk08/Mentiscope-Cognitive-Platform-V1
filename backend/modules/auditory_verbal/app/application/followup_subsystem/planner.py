"""
Module 3: Deterministic Adaptive Follow-up Planner.
Applies deterministic strategy rules to construct an immutable FollowUpSpecification.
"""

from typing import List, Dict, Any, Optional
from app.application.followup_subsystem.specification import FollowUpSpecification
from app.application.followup_subsystem.construct_analyzer import ConstructCoverageMatrix
from app.application.followup_subsystem.evidence_extractor import EvidenceItem


class AdaptiveFollowUpPlanner:
    """Deterministic strategy engine deciding follow-up intent and target construct without LLM."""

    def plan_followup(
        self,
        coverage_matrix: ConstructCoverageMatrix,
        transcript_text: str,
        target_constructs: List[str],
        evidence_items: List[EvidenceItem],
        turn_number: int = 1,
        conversation_stage: str = "ADAPTIVE_FOLLOWUP",
    ) -> FollowUpSpecification:

        clean_text = (transcript_text or "").strip()

        # Rule 1: Invalid or Ambiguous Transcript
        if len(clean_text) < 15 or clean_text.lower() in ["hello", "yes", "no", "i don't know", "abc", "maybe"]:
            target_c = target_constructs[0] if target_constructs else "COMMUNICATION"
            return FollowUpSpecification(
                intent="CLARIFY_AMBIGUITY",
                target_construct=target_c,
                reason="Candidate response is brief or ambiguous; clarification required.",
                context_snippet=clean_text,
                cognitive_depth="CLARIFICATION",
                conversation_stage=conversation_stage,
                turn_number=turn_number,
                metadata={"rule_applied": "RULE_1_AMBIGUOUS_RESPONSE"},
            )

        # Rule 2: Primary Deficit Construct (Missing Evidence)
        if coverage_matrix.missing_constructs:
            target_c = coverage_matrix.primary_deficit_construct
            quote = evidence_items[0].verbatim_quote if evidence_items else clean_text[:100]
            return FollowUpSpecification(
                intent="PROBE_MISSING_CONSTRUCT",
                target_construct=target_c,
                reason=f"Insufficient evidence collected for construct '{target_c}'; targeted probe required.",
                context_snippet=quote,
                cognitive_depth="CONSTRUCT_EXPLORATION",
                conversation_stage=conversation_stage,
                turn_number=turn_number,
                metadata={"rule_applied": "RULE_2_MISSING_CONSTRUCT"},
            )

        # Rule 3: Challenge Reasoning on Key Decision/Trade-off
        if "REASONING" in target_constructs or "DECISION_MAKING" in target_constructs:
            target_c = "REASONING" if "REASONING" in target_constructs else "DECISION_MAKING"
            quote = evidence_items[0].verbatim_quote if evidence_items else clean_text[:100]
            return FollowUpSpecification(
                intent="CHALLENGE_REASONING",
                target_construct=target_c,
                reason=f"Candidate stated initial strategy; challenging decision trade-offs for '{target_c}'.",
                context_snippet=quote,
                cognitive_depth="TRADE_OFF_DEFENSE",
                conversation_stage=conversation_stage,
                turn_number=turn_number,
                metadata={"rule_applied": "RULE_3_CHALLENGE_REASONING"},
            )

        # Rule 4: Metacognitive Reflection & Rationale Defense
        target_c = target_constructs[0] if target_constructs else "COMMUNICATION"
        quote = evidence_items[0].verbatim_quote if evidence_items else clean_text[:100]
        return FollowUpSpecification(
            intent="METACOGNITIVE_REFLECTION",
            target_construct=target_c,
            reason=f"Construct evidence saturated; probing metacognitive reflection for '{target_c}'.",
            context_snippet=quote,
            cognitive_depth="REFLECTION_JUSTIFICATION",
            conversation_stage=conversation_stage,
            turn_number=turn_number,
            metadata={"rule_applied": "RULE_4_METACOGNITIVE_REFLECTION"},
        )
