"""
Assessment Compiler Component.
Converts Layer 1 (Assessment Skeleton), Layer 2 (Scenario Skeleton), Layer 3 (Scenario Grammar),
and Layer 4 (Interaction Model) into a fully specified AssessmentSpecification.
"""

from typing import Tuple
from app.application.scenario_subsystem.assessment_skeleton import AssessmentSkeleton
from app.application.scenario_subsystem.scenario_skeleton import ScenarioSkeleton
from app.application.scenario_subsystem.scenario_grammar import ScenarioGrammar
from app.application.scenario_subsystem.interaction_model import InteractionModel
from app.application.scenario_subsystem.assessment_specification import (
    AssessmentSpecification,
    NarrativePlan,
    NarrativeBeat,
    ListeningPlan,
    MCQSpecification,
    SpeakingPlan,
    SpeakingSpecification,
    StructuralFingerprint,
)


class AssessmentCompiler:
    """Compiles 4 planning layers into an explicit, deterministic AssessmentSpecification."""

    def compile(
        self,
        assessment_skel: AssessmentSkeleton,
        scenario_skel: ScenarioSkeleton,
        grammar: ScenarioGrammar,
        interaction: InteractionModel,
    ) -> AssessmentSpecification:

        # 1. Build Extensible NarrativePlan from NarrativeBeats
        beats = (
            NarrativeBeat(
                purpose="SETTING",
                focus=f"Establish physical setting in '{scenario_skel.setting}' and primary objective '{scenario_skel.primary_objective}'.",
                stakeholder_ref=scenario_skel.primary_stakeholder,
            ),
            NarrativeBeat(
                purpose="STAKEHOLDER_SETUP",
                focus=f"Introduce primary stakeholder '{scenario_skel.primary_stakeholder}' and secondary '{scenario_skel.secondary_stakeholder}' dynamics.",
                stakeholder_ref=f"{scenario_skel.primary_stakeholder} & {scenario_skel.secondary_stakeholder}",
            ),
            NarrativeBeat(
                purpose="TRIGGER",
                focus=f"Reveal trigger event '{scenario_skel.trigger_event}' under operational constraint '{scenario_skel.operational_constraint}'.",
                stakeholder_ref=scenario_skel.primary_stakeholder,
            ),
            NarrativeBeat(
                purpose="ESCALATION",
                focus=f"Unfold escalation event '{scenario_skel.escalation_event}' with time pressure '{scenario_skel.time_pressure}'.",
                stakeholder_ref=scenario_skel.secondary_stakeholder,
            ),
            NarrativeBeat(
                purpose="DECISION_POINT",
                focus=f"Formulate trade-off decision considering failure risk '{scenario_skel.failure_risk}'.",
                stakeholder_ref=scenario_skel.primary_stakeholder,
            ),
        )
        narrative_plan = NarrativePlan(beats=beats)

        # 2. Build ListeningPlan (4 Structured MCQ Specifications)
        mcq_specs = (
            MCQSpecification(
                question_number=1,
                target_construct=assessment_skel.primary_constructs[0] if assessment_skel.primary_constructs else "WORKING_MEMORY",
                cognitive_depth="RECALL",
                prompt_intent=f"Recall primary operational constraint regarding '{scenario_skel.operational_constraint}'.",
            ),
            MCQSpecification(
                question_number=2,
                target_construct="ATTENTION",
                cognitive_depth="INFERENCE",
                prompt_intent=f"Infer the immediate impact of trigger event '{scenario_skel.trigger_event}'.",
            ),
            MCQSpecification(
                question_number=3,
                target_construct="LISTENING_ABILITY",
                cognitive_depth="PRIORITY",
                prompt_intent=f"Identify the primary domain requirement for category '{scenario_skel.category}'.",
            ),
            MCQSpecification(
                question_number=4,
                target_construct="REASONING",
                cognitive_depth="DECISION",
                prompt_intent=f"Determine the correct protocol to prevent failure risk '{scenario_skel.failure_risk}'.",
            ),
        )
        listening_plan = ListeningPlan(mcqs=mcq_specs)

        # 3. Build SpeakingPlan (3 Explicit EDAPAF Stage Specifications)
        speaking_specs = (
            SpeakingSpecification(
                stage_number=1,
                stage_name="Initial Decision Strategy",
                target_constructs=tuple(assessment_skel.primary_constructs),
                prompt_intent=f"Explain candidate's initial strategy to resolve '{scenario_skel.trigger_event}' within '{scenario_skel.time_pressure}'.",
            ),
            SpeakingSpecification(
                stage_number=2,
                stage_name="Adaptive Resource Challenge",
                target_constructs=tuple(assessment_skel.secondary_constructs or assessment_skel.primary_constructs),
                prompt_intent=f"Navigate escalation event '{scenario_skel.escalation_event}' when missing '{scenario_skel.missing_resources[0] if scenario_skel.missing_resources else 'key components'}'.",
            ),
            SpeakingSpecification(
                stage_number=3,
                stage_name="Metacognitive Rationale & Reflection",
                target_constructs=tuple(assessment_skel.primary_constructs),
                prompt_intent=f"Reflect on trade-off decision and justify rationale regarding theme '{scenario_skel.reflection_theme}'.",
            ),
        )
        speaking_plan = SpeakingPlan(prompts=speaking_specs)

        # 4. Build Rich StructuralFingerprint
        fingerprint = StructuralFingerprint(
            intent=scenario_skel.scenario_intent,
            grammar=grammar.name,
            interaction=interaction.name,
            decision_type=scenario_skel.expected_decision_type,
            stakeholder_pattern=f"{scenario_skel.primary_stakeholder} -> {scenario_skel.secondary_stakeholder}",
            resource_pattern=f"Available:{len(scenario_skel.available_resources)}|Missing:{len(scenario_skel.missing_resources)}",
            escalation_pattern=scenario_skel.escalation_event[:40],
            narrative_pattern=f"{grammar.name}:{len(beats)}_beats",
            mcq_pattern="|".join(m.target_construct for m in mcq_specs),
            speaking_pattern="|".join(p.stage_name for p in speaking_specs),
        )

        return AssessmentSpecification(
            assessment_skeleton=assessment_skel,
            scenario_skeleton=scenario_skel,
            grammar=grammar,
            interaction_model=interaction,
            narrative_plan=narrative_plan,
            listening_plan=listening_plan,
            speaking_plan=speaking_plan,
            fingerprint=fingerprint,
        )
