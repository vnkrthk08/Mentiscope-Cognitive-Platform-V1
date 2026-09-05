"""
Stage 3: Evidence Gap Detector for Adaptive Follow-up Planning Layer.
Produces two ranked lists (primary_gaps, secondary_gaps) sorted lowest-confidence-first.
"""

import logging
from typing import Dict, List, Any, Tuple
from app.application.followup_subsystem.config import STATUS_MISSING, STATUS_WEAK
from app.application.followup_subsystem.session_state import FollowUpSessionState

logger = logging.getLogger(__name__)


class AdaptiveGapDetector:
    """Produces ranked lists of primary and secondary construct gaps."""

    def detect_gaps(
        self, session_state: FollowUpSessionState
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Returns (primary_gaps, secondary_gaps) where each gap item contains:
        {"construct": name, "confidence": score, "status": status}
        Sorted lowest-confidence-first.
        """
        coverage = session_state.construct_coverage

        primary_gaps: List[Dict[str, Any]] = []
        for c in session_state.primary_constructs:
            item = coverage.get(c)
            if item and item.status in (STATUS_MISSING, STATUS_WEAK):
                primary_gaps.append({
                    "construct": c,
                    "confidence": item.confidence,
                    "status": item.status,
                })

        secondary_gaps: List[Dict[str, Any]] = []
        for c in session_state.secondary_constructs:
            item = coverage.get(c)
            if item and item.status in (STATUS_MISSING, STATUS_WEAK):
                secondary_gaps.append({
                    "construct": c,
                    "confidence": item.confidence,
                    "status": item.status,
                })

        # Sort lowest-confidence-first
        primary_gaps.sort(key=lambda x: x["confidence"])
        secondary_gaps.sort(key=lambda x: x["confidence"])

        return primary_gaps, secondary_gaps
