"""TraceBuilderService — Generates DAG trace graphs of nodes and edges for an assessment."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.actp.services.audit_collector_service import AuditCollectorService
from app.domain.actp.entities.trace_node import TraceNode
from app.domain.actp.entities.trace_edge import TraceEdge


class TraceBuilderService:
    """Constructs Directed Acyclic Graph (DAG) trace graph of nodes & edges for an assessment."""

    def __init__(self, session: AsyncSession) -> None:
        self._collector = AuditCollectorService(session)

    async def generate_trace(self, assessment_id: str) -> Dict[str, Any]:
        audit_session = await self._collector.get_or_reconstruct_session(assessment_id)
        if not audit_session:
            raise ValueError(f"No audit records found for assessment '{assessment_id}'.")

        nodes: List[TraceNode] = []
        edges: List[TraceEdge] = []

        prev_node_id: Optional[str] = None

        for ev in audit_session.events:
            node_id = f"node-{ev.event_id[:8]}"
            node = TraceNode(
                node_id=node_id,
                node_type=self._get_node_type(ev.event_type),
                label=ev.event_type.replace("_", " ").title(),
                stage=ev.stage_name,
                status="COMPLETED",
                details=ev.payload,
                timestamp=ev.timestamp,
            )
            nodes.append(node)

            if prev_node_id:
                edge = TraceEdge(
                    source_node_id=prev_node_id,
                    target_node_id=node_id,
                    relation_type=self._get_relation_type(ev.event_type),
                    description=f"Flow from {prev_node_id} to {node_id}",
                )
                edges.append(edge)

            prev_node_id = node_id

        return {
            "assessment_id": audit_session.assessment_id,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "nodes": [n.to_dict() for n in nodes],
            "edges": [e.to_dict() for e in edges],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _get_node_type(self, event_type: str) -> str:
        mapping = {
            "ASSESSMENT_CREATED": "ASSESSMENT",
            "AUDIO_UPLOADED": "AUDIO",
            "SPEECH_PROCESSED": "SPEECH",
            "PROMPT_EXECUTED": "PROMPT",
            "EVIDENCE_EXTRACTED": "EVIDENCE",
            "CONSTRUCT_EVALUATED": "CONSTRUCT",
            "ASSESSMENT_SCORED": "SCORE",
            "REPORT_GENERATED": "REPORT",
            "RESEARCH_DATASET_CREATED": "RESEARCH_DATASET",
            "EXPERT_REVIEW": "EXPERT_REVIEW",
            "EXPERIMENT_COMPARISON": "EXPERIMENT_COMPARISON",
        }
        return mapping.get(event_type, "ARTIFACT")

    def _get_relation_type(self, event_type: str) -> str:
        mapping = {
            "AUDIO_UPLOADED": "UPLOADS_AUDIO",
            "SPEECH_PROCESSED": "TRANSCRIPTS_AUDIO",
            "PROMPT_EXECUTED": "EXECUTES_PROMPT",
            "EVIDENCE_EXTRACTED": "EXTRACTS_EVIDENCE",
            "CONSTRUCT_EVALUATED": "EVALUATES_CONSTRUCT",
            "ASSESSMENT_SCORED": "SCORES_ASSESSMENT",
            "REPORT_GENERATED": "GENERATES_REPORT",
            "RESEARCH_DATASET_CREATED": "BUILDS_RESEARCH_DATASET",
            "EXPERT_REVIEW": "REVIEWS_DATASET",
            "EXPERIMENT_COMPARISON": "COMPARES_EXPERIMENT",
        }
        return mapping.get(event_type, "DEPENDS_ON")
