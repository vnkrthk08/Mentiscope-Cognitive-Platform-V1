from typing import Dict, List, Any
from app.domain.entities.behavioural_indicator import BehaviouralIndicator
from app.domain.value_objects.enums import ConstructType


CANONICAL_SQ1_INDICATORS: List[BehaviouralIndicator] = [
    BehaviouralIndicator(
        indicator_id="SQ1_IND_1",
        name="Makes a clear decision",
        weight=1.0,
        scale="0-4",
        anchors={
            "0": "Fails to state a choice or remains completely undecided.",
            "1": "Hesitantly leans toward an option with vague commitment.",
            "2": "States an identifiable choice but with ambiguity.",
            "3": "Clearly and unambiguously declares a specific choice.",
            "4": "Decisively states a well-defined decision with immediate clarity.",
        },
    ),
    BehaviouralIndicator(
        indicator_id="SQ1_IND_2",
        name="Gives logical justification",
        weight=1.0,
        scale="0-4",
        anchors={
            "0": "Provides no reasons or contradictory logic.",
            "1": "Gives superficial reasons with weak causal connection.",
            "2": "Provides basic logical reasoning supporting the choice.",
            "3": "Presents structured, relevant logical arguments tied to scenario facts.",
            "4": "Delivers a compelling, highly structured justification.",
        },
    ),
    BehaviouralIndicator(
        indicator_id="SQ1_IND_3",
        name="Considers consequences",
        weight=0.8,
        scale="0-4",
        anchors={
            "0": "Completely ignores potential negative outcomes.",
            "1": "Mentions consequences only in a superficial manner.",
            "2": "Identifies at least one direct consequence.",
            "3": "Evaluates meaningful direct and indirect consequences.",
            "4": "Thoroughly analyzes multi-dimensional short- and long-term impacts.",
        },
    ),
    BehaviouralIndicator(
        indicator_id="SQ1_IND_4",
        name="Considers alternatives",
        weight=0.8,
        scale="0-4",
        anchors={
            "0": "Ignores alternative options completely.",
            "1": "Mentions an alternative without evaluating it.",
            "2": "Briefly compares the chosen option against one alternative.",
            "3": "Weighs the chosen option against viable alternatives.",
            "4": "Systematically compares multiple alternatives.",
        },
    ),
    BehaviouralIndicator(
        indicator_id="SQ1_IND_5",
        name="Gives feasible action plan",
        weight=1.0,
        scale="0-4",
        anchors={
            "0": "Provides no practical next steps.",
            "1": "Proposes vague or unrealistic steps.",
            "2": "Outlines basic actionable steps with minor feasibility gaps.",
            "3": "Delivers a practical, sequentially sound action plan.",
            "4": "Provides a comprehensive, highly feasible step-by-step roadmap.",
        },
    ),
]

CANONICAL_SQ2_INDICATORS: List[BehaviouralIndicator] = [
    BehaviouralIndicator(
        indicator_id="SQ2_IND_1",
        name="Acknowledges the new complication",
        weight=1.0,
        scale="0-4",
        anchors={
            "0": "Fails to acknowledge or completely ignores the newly introduced complication.",
            "1": "Vaguely mentions an issue but misidentifies or misinterprets the core constraint.",
            "2": "Accurately identifies the complication at a surface level.",
            "3": "Explicitly identifies the new complication and describes its disruption to the plan.",
            "4": "Precisely and thoroughly articulates the new complication, identifying immediate and secondary bottlenecks.",
        },
    ),
    BehaviouralIndicator(
        indicator_id="SQ2_IND_2",
        name="Modifies approach in response to change",
        weight=1.0,
        scale="0-4",
        anchors={
            "0": "Rigidly insists on the original plan or displays complete decision paralysis.",
            "1": "Proposes superficial adjustments while clinging to the unworkable plan.",
            "2": "Proposes a partial pivot but retains components that conflict with the new complication.",
            "3": "Clearly adapts the approach, pivoting to a revised strategy that accommodates the new condition.",
            "4": "Seamlessly executes a comprehensive strategic pivot, integrating new methods to neutralize the complication.",
        },
    ),
    BehaviouralIndicator(
        indicator_id="SQ2_IND_3",
        name="Prioritizes the most critical constraint",
        weight=0.8,
        scale="0-4",
        anchors={
            "0": "Shows no prioritization; fixates on irrelevant background details.",
            "1": "Misallocates focus to secondary matters while neglecting the primary operational bottleneck.",
            "2": "Identifies the main constraint but allocates equal attention to minor issues.",
            "3": "Accurately isolates and prioritizes the primary constraint created by the new complication.",
            "4": "Decisively triages conflicting demands, establishing a clear hierarchy of immediate urgency vs. secondary needs.",
        },
    ),
    BehaviouralIndicator(
        indicator_id="SQ2_IND_4",
        name="Explains rationale for adaptation",
        weight=0.8,
        scale="0-4",
        anchors={
            "0": "Provides no rationale or gives contradictory and incoherent reasoning.",
            "1": "Gives a superficial reason without linking it causally to the complication.",
            "2": "Explains basic logic but the causal link to the new constraint is incomplete.",
            "3": "Clearly explains why the adapted approach is necessary and how it directly responds to the new constraint.",
            "4": "Articulates a structured, persuasive rationale demonstrating why the adapted path outperforms alternatives.",
        },
    ),
    BehaviouralIndicator(
        indicator_id="SQ2_IND_5",
        name="Provides a feasible revised action",
        weight=1.0,
        scale="0-4",
        anchors={
            "0": "Offers no actionable steps or proposes an impossible/hazardous action violating new constraints.",
            "1": "Suggests vague or wishful steps lacking operational viability.",
            "2": "Proposes a workable action but overlooks realistic resource, time, or stakeholder limitations.",
            "3": "Outlines a concrete, realistic action plan executable within newly imposed constraints.",
            "4": "Delivers a highly structured, step-by-step action plan with realistic sequencing and immediate operational readiness.",
        },
    ),
]

CANONICAL_SQ3_INDICATORS: List[BehaviouralIndicator] = [
    BehaviouralIndicator(
        indicator_id="SQ3_IND_1",
        name="Evaluates trade-offs and compromises",
        weight=1.0,
        scale="0-4",
        anchors={
            "0": "Denies trade-offs existed or ignores compromises made.",
            "1": "Acknowledges a downside in a trivial manner without comparing it against what was gained.",
            "2": "Identifies a trade-off but provides only a surface-level contrast between gains and losses.",
            "3": "Clearly articulates key trade-offs, contrasting what was sacrificed against what was preserved.",
            "4": "Insightfully analyzes multi-dimensional trade-offs across competing priorities and short- vs. long-term goals.",
        },
    ),
    BehaviouralIndicator(
        indicator_id="SQ3_IND_2",
        name="Examines underlying assumptions or limitations",
        weight=0.8,
        scale="0-4",
        anchors={
            "0": "Displays zero awareness of underlying assumptions, treating all personal premises as undisputed facts.",
            "1": "Mentions an external constraint but mistakes it for an internal assumption; lacks critical introspection.",
            "2": "Identifies a premise or boundary condition, but does not explore how it could have failed.",
            "3": "Explicitly identifies key assumptions or operational boundaries that governed the decision.",
            "4": "Rigorously interrogates foundational assumptions and potential blind spots, explaining points of vulnerability.",
        },
    ),
    BehaviouralIndicator(
        indicator_id="SQ3_IND_3",
        name="Analyzes broader consequences and ripple effects",
        weight=1.0,
        scale="0-4",
        anchors={
            "0": "Fails to see beyond the immediate moment; oblivious to secondary or downstream effects.",
            "1": "Mentions an immediate direct consequence only, ignoring wider stakeholder or systemic ripple effects.",
            "2": "Notes secondary effects on one isolated stakeholder or metric, but lacks systemic depth.",
            "3": "Evaluates meaningful downstream effects on stakeholders, timelines, institutional trust, or safety.",
            "4": "Conducts a systemic analysis of cascading short- and long-term consequences across all affected parties.",
        },
    ),
    BehaviouralIndicator(
        indicator_id="SQ3_IND_4",
        name="Identifies improvements or alternatives in hindsight",
        weight=0.8,
        scale="0-4",
        anchors={
            "0": "Defensively insists no improvement was possible, or exhibits unconstructive despair.",
            "1": "Offers generic clichés without concrete procedural substance.",
            "2": "Suggests a plausible minor adjustment, but overlooks root procedural bottlenecks.",
            "3": "Articulates concrete, actionable procedural adjustments that would have improved efficiency or mitigated the crisis earlier.",
            "4": "Pinpoints root-cause procedural optimizations and proactive contingency frameworks that elevate the response system.",
        },
    ),
    BehaviouralIndicator(
        indicator_id="SQ3_IND_5",
        name="Extracts a transferable principle or lesson",
        weight=1.0,
        scale="0-4",
        anchors={
            "0": "Extracts no lesson or states an irrelevant platitude disconnected from the experience.",
            "1": "States a hyper-specific recap that cannot be applied beyond this exact narrow instance.",
            "2": "States a broad generic rule lacking operational depth.",
            "3": "Distills a well-defined transferable principle linking situational dynamics to future decision contexts.",
            "4": "Formulates an actionable, sophisticated heuristic for governance, risk management, or crisis leadership.",
        },
    ),
]


CANONICAL_SPEAKING_SPECS: Dict[str, Dict[str, Any]] = {
    "SQ1": {
        "question_id": "SQ1",
        "stage": "STAGE_1_DECISION",
        "primary_constructs": [ConstructType.DECISION_MAKING],
        "secondary_constructs": [ConstructType.COMMUNICATION],
        "objective": "Evaluate whether the candidate can make, justify, and plan a feasible decision under situational constraints.",
        "behavioural_indicators": CANONICAL_SQ1_INDICATORS,
        "max_indicator_weighted_score": 18.4,
    },
    "SQ2": {
        "question_id": "SQ2",
        "stage": "STAGE_2_CHALLENGE",
        "primary_constructs": [ConstructType.ADAPTABILITY],
        "secondary_constructs": [ConstructType.DECISION_MAKING],
        "objective": "Evaluate whether the candidate can recognize a new situational complication, pivot their approach, prioritize emerging constraints, explain the rationale for adapting, and formulate a feasible revised action.",
        "behavioural_indicators": CANONICAL_SQ2_INDICATORS,
        "max_indicator_weighted_score": 18.4,
    },
    "SQ3": {
        "question_id": "SQ3",
        "stage": "STAGE_3_REFLECTIVE",
        "primary_constructs": [ConstructType.REASONING],
        "secondary_constructs": [ConstructType.COMMUNICATION],
        "objective": "Evaluate whether the candidate can perform retrospective reasoning on their choices by evaluating trade-offs, interrogating assumptions or limitations, assessing downstream consequences, and synthesizing transferable principles.",
        "behavioural_indicators": CANONICAL_SQ3_INDICATORS,
        "max_indicator_weighted_score": 18.4,
    },
}
