"""
Module: Interview Analytics Collector (v5).
Tracks behavioral evidence growth, construct saturation curves, contradiction frequencies, and closure telemetry.
"""

from typing import Dict, Any, List
from app.application.followup_subsystem.closure_engine import ClosureDecision, ConstructSaturationMetrics


class InterviewAnalyticsCollector:
    """Telemetry collector for evidence graph analytics, saturation curves, and closure statistics."""

    _session_records: Dict[str, List[Dict[str, Any]]] = {}

    @classmethod
    def record_turn_telemetry(
        self,
        session_id: str,
        turn_number: int,
        closure_decision: ClosureDecision,
        saturation_matrix: Dict[str, ConstructSaturationMetrics],
        node_count: int,
        edge_count: int,
    ):
        if session_id not in self._session_records:
            self._session_records[session_id] = []

        self._session_records[session_id].append({
            "turn_number": turn_number,
            "should_close": closure_decision.should_close,
            "saturation_percentage": closure_decision.saturation_percentage,
            "completion_percentage": closure_decision.completion_percentage,
            "unresolved_contradictions": closure_decision.unresolved_contradictions_count,
            "graph_nodes": node_count,
            "graph_edges": edge_count,
            "saturation_matrix": {c: m.saturation_score for c, m in saturation_matrix.items()},
        })

    @classmethod
    def generate_analytics_report(self) -> Dict[str, Any]:
        total_sessions = len(self._session_records)
        if total_sessions == 0:
            return {"status": "NO_TELEMETRY_DATA"}

        total_turns = sum(len(turns) for turns in self._session_records.values())
        closed_sessions = sum(1 for turns in self._session_records.values() if any(t["should_close"] for t in turns))
        avg_turns_to_closure = round(total_turns / total_sessions, 1)

        return {
            "total_sessions_tracked": total_sessions,
            "total_turns_recorded": total_turns,
            "closed_sessions_count": closed_sessions,
            "average_questions_per_interview": avg_turns_to_closure,
            "average_closure_turn": avg_turns_to_closure,
        }
