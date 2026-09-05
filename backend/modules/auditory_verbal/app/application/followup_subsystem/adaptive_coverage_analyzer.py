"""
Stage 2: Construct Coverage Analyzer for Adaptive Follow-up Planning Layer.
Deterministic additive scoring mapping extracted evidence items against construct behavioral indicators.
"""

import logging
from typing import Dict, List, Any, Optional

from app.application.followup_subsystem.config import (
    EVIDENCE_CONFIDENCE_INCREMENT,
    MAX_CONSTRUCT_CONFIDENCE,
)
from app.application.followup_subsystem.session_state import (
    FollowUpSessionState,
    ConstructCoverageItem,
    EvidenceLogEntry,
)
from app.infrastructure.persistence.repositories.construct_repository import ConstructRepository

logger = logging.getLogger(__name__)


# Domain mapping of construct names to explicit indicators and domain keywords
CONSTRUCT_INDICATORS_AND_KEYWORDS: Dict[str, Dict[str, List[str]]] = {
    "DECISION_MAKING": {
        "indicators": [
            "Emergency Protocol Initiation",
            "Safety Prioritization",
            "Risk Mitigation",
            "Trade-off Evaluation",
            "Resource Allocation",
            "Decision Rationale",
        ],
        "keywords": [
            "decided", "decision", "trade-off", "tradeoff", "choose", "chose",
            "choice", "option", "reroute", "re-route", "priority", "prioritize", "balance"
        ],
    },
    "REASONING": {
        "indicators": [
            "Logical Inference",
            "Consequence Analysis",
            "Critical Evaluation",
            "Adaptation Strategy",
            "Root Cause Analysis",
        ],
        "keywords": [
            "because", "since", "due to", "rationale", "disqualification", "prevent",
            "allow us to", "allows us", "means that", "in order to", "so that", "therefore",
            "thus", "result", "disqualification", "time limit"
        ],
    },
    "ATTENTION": {
        "indicators": [
            "Focused Detail Identification",
            "Operational Constraint Focus",
            "Selective Information Processing",
            "Setting Detail Focus",
        ],
        "keywords": [
            "09:15", "65°c", "65 degrees", "50 minutes", "45 minutes", "10:00",
            "20%", "75%", "92%", "88%", "₹2,000", "2,000", "3 trial passes", "term 1", "5-year"
        ],
    },
    "COMMUNICATION": {
        "indicators": [
            "Logical Sequencing",
            "Articulate Response",
            "Clarity of Expression",
            "Stakeholder Alignment",
            "Structured Argumentation",
        ],
        "keywords": [
            "meeting", "father", "present", "roadmap", "reassure", "explain",
            "pitch", "counselor", "ms. ritu", "dr. arora", "mr. gupta", "parents",
            "dialogue", "joint meeting"
        ],
    },
    "LEADERSHIP": {
        "indicators": [
            "Team Coordination",
            "Role Delegation",
            "Accountability Enforcement",
            "Consensus Building",
        ],
        "keywords": [
            "president", "eco-club", "banned", "lead", "leading", "enforced",
            "stewardship", "coordination", "initiative"
        ],
    },
    "PROBLEM_SOLVING": {
        "indicators": [
            "Root Cause Analysis",
            "Systematic Troubleshooting",
            "Contingency Execution",
            "Alternative Evaluation",
        ],
        "keywords": [
            "refill stations", "pta sponsorship", "logistics", "solution", "resolve",
            "proposed", "alternative", "reusable", "deposit"
        ],
    },
    "WORKING_MEMORY": {
        "indicators": [
            "Detail Retention",
            "Sequential Recall",
            "Verbatim Fact Recall",
            "Parameter Retention",
        ],
        "keywords": [
            "retained", "recalled", "remembered", "verbatim", "exact figure", "exact time"
        ],
    },
    "EMOTIONAL_REGULATION": {
        "indicators": [
            "Composure Under Pressure",
            "De-escalation",
            "Constructive Mindset",
            "Conflict Resolution",
        ],
        "keywords": [
            "calm", "de-escalate", "composure", "patience", "handled objection", "reassure"
        ],
    },
}


class AdaptiveCoverageAnalyzer:
    """Evaluates accumulated evidence entries against target constructs using domain behavioral indicators."""

    def __init__(self, construct_repo: Optional[ConstructRepository] = None):
        self.construct_repo = construct_repo

    def analyze_coverage(
        self,
        session_state: FollowUpSessionState,
        latest_entry: Optional[EvidenceLogEntry] = None,
    ) -> Dict[str, ConstructCoverageItem]:
        """Updates construct_coverage in session_state using extracted evidence and domain behavioral indicators."""
        target_constructs = list(dict.fromkeys(session_state.primary_constructs + session_state.secondary_constructs))

        for c_name in target_constructs:
            if c_name not in session_state.construct_coverage:
                session_state.construct_coverage[c_name] = ConstructCoverageItem()

            item = session_state.construct_coverage[c_name]
            c_info = CONSTRUCT_INDICATORS_AND_KEYWORDS.get(c_name.upper(), {
                "indicators": ["Observed behavior"],
                "keywords": [c_name.lower().replace("_", " ")]
            })

            indicators = [ind.lower() for ind in c_info["indicators"]]
            keywords = [kw.lower() for kw in c_info["keywords"]]

            matching_refs = set()

            for entry in session_state.evidence_log:
                ref_id = f"turn_{entry.turn}"
                combined_text = " ".join(entry.claims + entry.reasoning_shown + entry.assumptions).lower()

                # Check if combined text contains any matching indicators or keywords for this construct
                indicator_match = any(ind in combined_text for ind in indicators)
                keyword_match = any(kw in combined_text for kw in keywords)

                if indicator_match or keyword_match:
                    matching_refs.add(ref_id)

            item.evidence_refs = sorted(list(matching_refs))
            match_count = len(item.evidence_refs)
            raw_conf = min(match_count * EVIDENCE_CONFIDENCE_INCREMENT, MAX_CONSTRUCT_CONFIDENCE)
            item.confidence = round(raw_conf, 2)
            item.update_status()

        return session_state.construct_coverage
