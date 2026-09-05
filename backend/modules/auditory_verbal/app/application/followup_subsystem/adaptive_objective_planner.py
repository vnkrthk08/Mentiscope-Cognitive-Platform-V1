"""
Stage 4: Follow-up Objective Planner for the Adaptive Follow-up Engine.

Deterministic, data-driven planner that selects the next follow-up objective
and target constructs based on Stage 3 evidence gaps, signal triggers, and
session history.

Design Notes:
  - Tie-break rule: rank_key = (confidence ASC, -status_priority, declared_order_index).
    "missing" has higher status_priority than "weak". On ties, declared order in
    the scenario's primary_constructs / secondary_constructs list wins.
  - "Time Pressure" and "Resource Limitation" are CONSTRAINT-type concepts, not
    objectives. They appear only in the Stage 5 `constraints` array, never as
    an `objective` value.
  - Open dependency on Stage 2 confidence semantics: This module assumes
    construct_coverage.confidence reflects construct-specific, evidence-indexed
    scoring — i.e. confidence only increases for a construct when that specific
    construct's behavioral indicators are matched in the turn's evidence. If
    Stage 2 increments confidence for co-occurring but untargeted constructs in
    lockstep, Stage 4's ranking operates on a corrupted signal. This remains an
    open upstream verification task outside Stage 4's test suite.
  - difficulty mapping is an intentional v1 simplification: "Intermediate" for
    first probes, "Advanced" for repeats. Multi-tier depth-based scaling (e.g.
    Introductory → Intermediate → Advanced → Expert) is a known v2 enhancement.
  - `reflection` objective is deferred in this pass: marked status="deferred"
    in objective_catalog.json and excluded from active signal checking.
"""

import json
import logging
import os
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple

from app.application.followup_subsystem.config import STATUS_MISSING, STATUS_WEAK, STATUS_SUFFICIENT
from app.application.followup_subsystem.session_state import FollowUpSessionState, EvidenceLogEntry

logger = logging.getLogger(__name__)

# Status priority for tie-breaking: missing (highest priority) > weak > sufficient
_STATUS_PRIORITY = {
    STATUS_MISSING: 2,
    STATUS_WEAK: 1,
    STATUS_SUFFICIENT: 0,
}

# Signal-trigger priority order (highest first):
# 1. contradiction_detection — unresolved contradictions directly impact validity
# 2. confidence_verification — heavy hedging suggests uncertain commitment
_SIGNAL_PRIORITY = ["contradiction_detection", "confidence_verification"]

# Threshold: confidence_verification fires when a single turn's evidence
# contains >= this many distinct grounded hedging/stance markers.
HEDGE_TRIGGER_THRESHOLD = 2

# Default max follow-up turns per scenario before forced termination.
DEFAULT_MAX_FOLLOWUP_TURNS = 5


def rank_key(
    construct_name: str,
    confidence: float,
    status: str,
    declared_order_index: int,
) -> Tuple[float, int, int]:
    """
    Deterministic gap-ranking key for sorting constructs by priority.

    Sort ascending → lowest confidence first, then highest status priority
    (missing > weak), then declared order (lower index = earlier in scenario
    declaration = higher priority on tie).

    Returns a tuple suitable for sorted() / min():
        (confidence, -status_priority, declared_order_index)
    """
    sp = _STATUS_PRIORITY.get(status, 0)
    return (confidence, -sp, declared_order_index)


@dataclass
class FollowUpObjectiveDecision:
    """
    Stage 5 specification produced by the Follow-up Objective Planner.

    to_dict() emits the canonical 5-field Stage 5 JSON contract:
        objective, target_constructs, reason, difficulty, constraints

    Internal control attributes (is_repeat, is_terminate, termination_reason)
    are Python-only and NOT serialized into the Stage 5 JSON, preserving
    downstream contract integrity.
    """
    objective: str = ""
    target_constructs: List[str] = field(default_factory=list)
    reason: str = ""
    difficulty: str = "Intermediate"
    constraints: List[str] = field(default_factory=list)

    # Internal-only attributes — not serialized into Stage 5 JSON
    is_repeat: bool = False
    is_terminate: bool = False
    termination_reason: str = ""

    def __post_init__(self):
        # v1 simplification: difficulty derived from repeat status
        if self.is_repeat:
            self.difficulty = "Advanced"

    def to_dict(self) -> Dict[str, Any]:
        """Canonical 5-field Stage 5 JSON contract output."""
        return {
            "objective": self.objective,
            "target_constructs": self.target_constructs,
            "reason": self.reason,
            "difficulty": self.difficulty,
            "constraints": self.constraints,
        }


class AdaptiveObjectivePlanner:
    """
    Deterministic data-driven planner implementing the 4-step precedence pipeline:

    1. Check turn cap reached → terminate.
    2. Check signal triggers (contradiction_detection, confidence_verification)
       → select signal objective.
       Design decision: Signal pre-emption over sufficiency. Active contradictions
       or heavy hedging uttered on Turn N take precedence over background construct
       sufficiency to ensure active validity risks are probed before interview
       completion.
    3. Check all gaps sufficient → terminate.
    4. Run gap-ranked objective selection with escalation (Steps 4a-4d).
    """

    def __init__(
        self,
        catalog_file_path: Optional[str] = None,
        max_followup_turns: int = DEFAULT_MAX_FOLLOWUP_TURNS,
    ):
        self._catalog = self._load_catalog(catalog_file_path)
        self._max_followup_turns = max_followup_turns
        # Build reverse index: construct → list of applicable objectives
        self._construct_objectives: Dict[str, List[str]] = {}
        for obj_name, obj_info in self._catalog.items():
            if obj_info.get("type") == "construct_targeted":
                for c in obj_info.get("applicable_constructs", []):
                    self._construct_objectives.setdefault(c, []).append(obj_name)

    def _load_catalog(self, catalog_file_path: Optional[str] = None) -> Dict[str, Any]:
        if not catalog_file_path:
            catalog_file_path = os.path.join(
                os.path.dirname(__file__), "objective_catalog.json"
            )
        try:
            with open(catalog_file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("objectives", data)
        except Exception as err:
            logger.warning(f"[OBJECTIVE PLANNER] Failed to load catalog: {err}")
            return {}

    def get_candidate_objectives(self, construct_name: str) -> List[str]:
        """Returns ordered list of candidate objectives for a construct."""
        return list(self._construct_objectives.get(construct_name.upper(), []))

    def plan_objective(
        self,
        session_state: FollowUpSessionState,
        primary_gaps: List[Dict[str, Any]],
        secondary_gaps: List[Dict[str, Any]],
        turn_number: int = 0,
        scenario_constraints: Optional[List[str]] = None,
    ) -> FollowUpObjectiveDecision:
        """
        Main entry point. Executes the 4-step precedence pipeline.

        Args:
            session_state: Current FollowUpSessionState.
            primary_gaps: Stage 3 primary construct gaps (sorted by confidence).
            secondary_gaps: Stage 3 secondary construct gaps (sorted by confidence).
            turn_number: Current turn number (0-indexed or 1-indexed).
            scenario_constraints: Constraint-type flags from upstream scenario context
                                  (e.g. ["Time Pressure"]). Stage 4 selects from these
                                  — it does not invent new constraints.
        """
        used_objectives = set(
            item.get("objective", "") for item in session_state.followup_history
        )
        constraints = list(scenario_constraints) if scenario_constraints else []

        # ── Step 1: Turn Cap Check ──────────────────────────────────────────
        if turn_number > 0 and turn_number >= self._max_followup_turns:
            return FollowUpObjectiveDecision(
                is_terminate=True,
                termination_reason="Max turn cap reached",
                reason="Max turn cap reached",
                constraints=constraints,
            )

        # ── Step 2: Signal Trigger Check ────────────────────────────────────
        # Design decision: Signal pre-emption over sufficiency. Active
        # contradictions or heavy hesitations uttered on Turn N take precedence
        # over background construct sufficiency to ensure active validity risks
        # are probed before interview completion.
        signal_decision = self._check_signal_triggers(
            session_state, primary_gaps, secondary_gaps, used_objectives, constraints
        )
        if signal_decision is not None:
            return signal_decision

        # ── Step 3: All Gaps Sufficient Check ───────────────────────────────
        if not primary_gaps and not secondary_gaps:
            return FollowUpObjectiveDecision(
                is_terminate=True,
                termination_reason="All primary and secondary constructs sufficient",
                reason="All primary and secondary constructs sufficient",
                constraints=constraints,
            )

        # ── Step 4: Gap-Ranked Objective Selection ──────────────────────────
        return self._gap_ranked_selection(
            session_state, primary_gaps, secondary_gaps, used_objectives, constraints
        )

    def _check_signal_triggers(
        self,
        session_state: FollowUpSessionState,
        primary_gaps: List[Dict[str, Any]],
        secondary_gaps: List[Dict[str, Any]],
        used_objectives: set,
        constraints: List[str],
    ) -> Optional[FollowUpObjectiveDecision]:
        """
        Step 2: Check signal-triggered objectives in priority order.

        Priority:
          1. contradiction_detection (non-empty contradictions in latest evidence)
          2. confidence_verification (len(hedges) >= HEDGE_TRIGGER_THRESHOLD in latest evidence)
        """
        if not session_state.evidence_log:
            return None

        latest_entry = session_state.evidence_log[-1]

        # Signal 1: contradiction_detection
        if latest_entry.contradictions and len(latest_entry.contradictions) > 0:
            target_c = self._signal_target_constructs(
                session_state, primary_gaps, secondary_gaps
            )
            return FollowUpObjectiveDecision(
                objective="contradiction_detection",
                target_constructs=target_c,
                reason=(
                    f"Contradiction detected in turn {latest_entry.turn}: "
                    f"{latest_entry.contradictions[0]!r} — pre-empting normal "
                    f"gap ranking to resolve validity risk"
                ),
                constraints=constraints,
            )

        # Signal 2: confidence_verification
        if len(latest_entry.hedges) >= HEDGE_TRIGGER_THRESHOLD:
            target_c = self._signal_target_constructs(
                session_state, primary_gaps, secondary_gaps
            )
            return FollowUpObjectiveDecision(
                objective="confidence_verification",
                target_constructs=target_c,
                reason=(
                    f"Heavy hedging detected in turn {latest_entry.turn} "
                    f"({len(latest_entry.hedges)} markers: "
                    f"{latest_entry.hedges!r}) — probing commitment confidence"
                ),
                constraints=constraints,
            )

        return None

    def _signal_target_constructs(
        self,
        session_state: FollowUpSessionState,
        primary_gaps: List[Dict[str, Any]],
        secondary_gaps: List[Dict[str, Any]],
    ) -> List[str]:
        """
        Determine target_constructs for signal-triggered objectives.

        For contradiction_detection: ideally the construct(s) involved in the
        conflicting claims. Since Stage 1's contradictions field is a list of
        free-text strings without structured construct attribution, we fall back
        to the top-ranked primary gap (or secondary gap if no primary gaps).
        For confidence_verification: same — top-ranked gap construct.
        """
        if primary_gaps:
            return [primary_gaps[0]["construct"]]
        if secondary_gaps:
            return [secondary_gaps[0]["construct"]]
        # Fallback: first primary construct from scenario declaration
        if session_state.primary_constructs:
            return [session_state.primary_constructs[0]]
        return ["DECISION_MAKING"]

    def _gap_ranked_selection(
        self,
        session_state: FollowUpSessionState,
        primary_gaps: List[Dict[str, Any]],
        secondary_gaps: List[Dict[str, Any]],
        used_objectives: set,
        constraints: List[str],
    ) -> FollowUpObjectiveDecision:
        """
        Step 4: Gap-ranked objective selection with escalation.

        Sub-steps:
          4a. Build candidate_constructs from primary_gaps (if non-empty), else secondary_gaps.
          4b. Iterate candidate_constructs in rank order; find first construct with
              an un-exhausted objective.
          4c. (only if 4b succeeded) Check for dual-construct intersection with 2nd gap.
          4d. (only if 4b found nothing) Dead-end exhaustion fallback → terminate.
        """
        # ── 4a. Candidate Construct List ────────────────────────────────────
        if primary_gaps:
            gap_tier = "primary"
            candidate_constructs = self._sort_gaps_by_rank_key(
                primary_gaps, session_state.primary_constructs
            )
        else:
            gap_tier = "secondary"
            candidate_constructs = self._sort_gaps_by_rank_key(
                secondary_gaps, session_state.secondary_constructs
            )

        # ── 4b. Objective Exhaustion Escalation Loop ────────────────────────
        top_construct = None
        chosen_objective = None
        chosen_construct_idx = -1

        for idx, gap in enumerate(candidate_constructs):
            c_name = gap["construct"]
            candidate_objs = self.get_candidate_objectives(c_name)
            un_exhausted = [o for o in candidate_objs if o not in used_objectives]
            if un_exhausted:
                top_construct = gap
                chosen_objective = un_exhausted[0]
                chosen_construct_idx = idx
                break

        # ── 4d. Dead-End Exhaustion Fallback (4b found nothing) ─────────────
        if top_construct is None:
            return FollowUpObjectiveDecision(
                is_terminate=True,
                termination_reason="All candidate objectives for remaining construct gaps fully exhausted",
                reason="All candidate objectives for remaining construct gaps fully exhausted",
                constraints=constraints,
            )

        # ── 4c. Dual-Construct Intersection Check (4b succeeded) ────────────
        target_constructs = [top_construct["construct"]]
        dual_rationale = ""

        if len(candidate_constructs) >= 2:
            # Pick the 2nd-ranked gap (the next one after the chosen one)
            sec_idx = chosen_construct_idx + 1 if chosen_construct_idx + 1 < len(candidate_constructs) else -1
            if sec_idx == -1:
                sec_idx = 0 if chosen_construct_idx != 0 else -1

            if sec_idx >= 0 and sec_idx != chosen_construct_idx:
                sec_gap = candidate_constructs[sec_idx]
                sec_c = sec_gap["construct"]
                sec_objs = set(self.get_candidate_objectives(sec_c))

                # Check if the chosen_objective also applies to the 2nd construct
                if chosen_objective in sec_objs:
                    target_constructs = [top_construct["construct"], sec_c]
                    dual_rationale = (
                        f" — dual-construct coverage: '{chosen_objective}' also "
                        f"targets {sec_c} (confidence {sec_gap['confidence']:.2f}, "
                        f"{sec_gap['status']})"
                    )
                else:
                    # Check if any other un-exhausted objective of top_construct
                    # overlaps with 2nd construct
                    top_objs = self.get_candidate_objectives(top_construct["construct"])
                    top_un = [o for o in top_objs if o not in used_objectives]
                    shared = [o for o in top_un if o in sec_objs]
                    if shared:
                        chosen_objective = shared[0]
                        target_constructs = [top_construct["construct"], sec_c]
                        dual_rationale = (
                            f" — dual-construct coverage: switched to "
                            f"'{chosen_objective}' which also targets {sec_c}"
                        )
                    else:
                        dual_rationale = (
                            f" — no shared objective between "
                            f"{top_construct['construct']} and {sec_c}; "
                            f"falling back to single-construct targeting of "
                            f"{top_construct['construct']}"
                        )

        # ── Build decision ──────────────────────────────────────────────────
        is_repeat = chosen_objective in used_objectives
        reason = (
            f"{top_construct['construct']} confidence "
            f"{top_construct['confidence']:.2f} ({top_construct['status']}, "
            f"{gap_tier}) — "
        )
        if chosen_construct_idx > 0:
            reason += (
                f"escalated from exhausted higher-ranked gaps; "
                f"'{chosen_objective}' selected"
            )
        else:
            reason += f"lowest-ranked {gap_tier} gap; '{chosen_objective}' selected"
        reason += dual_rationale

        return FollowUpObjectiveDecision(
            objective=chosen_objective,
            target_constructs=target_constructs,
            reason=reason,
            is_repeat=is_repeat,
            constraints=constraints,
        )

    def _sort_gaps_by_rank_key(
        self,
        gaps: List[Dict[str, Any]],
        declared_order: List[str],
    ) -> List[Dict[str, Any]]:
        """Sort gap dicts by the deterministic rank_key."""
        order_map = {c: i for i, c in enumerate(declared_order)}
        return sorted(
            gaps,
            key=lambda g: rank_key(
                g["construct"],
                g["confidence"],
                g["status"],
                order_map.get(g["construct"], 999),
            ),
        )
