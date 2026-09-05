"""TimelineGenerator — Assembles chronological assessment lifecycle timeline."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.actp.services.audit_collector_service import AuditCollectorService
from app.domain.actp.entities.audit_session import AuditSession


class TimelineGenerator:
    """Generates the 12-stage chronological lifecycle timeline for an assessment."""

    def __init__(self, session: AsyncSession) -> None:
        self._collector = AuditCollectorService(session)

    async def generate_timeline(self, assessment_id: str) -> Dict[str, Any]:
        audit_session = await self._collector.get_or_reconstruct_session(assessment_id)
        if not audit_session:
            raise ValueError(f"No audit records found for assessment '{assessment_id}'.")

        steps = []
        for ev in audit_session.events:
            step_info = {
                "step_order": ev.step_order,
                "stage_name": ev.stage_name,
                "event_type": ev.event_type,
                "title": self._format_title(ev.event_type),
                "description": self._format_description(ev.event_type, ev.payload),
                "status": "COMPLETED",
                "timestamp": ev.timestamp.isoformat() if ev.timestamp else datetime.now(timezone.utc).isoformat(),
                "details": ev.payload,
            }
            steps.append(step_info)

        # Ensure sorted by step_order
        steps.sort(key=lambda x: x["step_order"])

        return {
            "assessment_id": audit_session.assessment_id,
            "candidate_id": audit_session.candidate_id,
            "scenario_id": audit_session.scenario_id,
            "total_steps": len(steps),
            "steps": steps,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def _format_title(self, event_type: str) -> str:
        mapping = {
            "ASSESSMENT_CREATED": "Assessment Created",
            "AUDIO_UPLOADED": "Audio Asset Uploaded",
            "SPEECH_PROCESSED": "Speech-to-Text Processed",
            "PROMPT_EXECUTED": "Prompt Context Executed",
            "EVIDENCE_EXTRACTED": "Behavior Evidence Extracted",
            "CONSTRUCT_EVALUATED": "Assessment Constructs Evaluated",
            "ASSESSMENT_SCORED": "Assessment Scored & Normalized",
            "REPORT_GENERATED": "Structured Report Generated",
            "RESEARCH_DATASET_CREATED": "Validation Dataset Built",
            "EXPERT_REVIEW": "Psychologist Expert Review",
            "EXPERIMENT_COMPARISON": "Model Governance Comparison",
        }
        return mapping.get(event_type, event_type.replace("_", " ").title())

    def _format_description(self, event_type: str, payload: Dict[str, Any]) -> str:
        if event_type == "ASSESSMENT_CREATED":
            return f"Session initialized for candidate {payload.get('candidate_id', '')} on scenario {payload.get('scenario_id', '')}."
        elif event_type == "SPEECH_PROCESSED":
            return f"Audio transcribed via {payload.get('stt_provider', 'STT')} (Confidence: {payload.get('confidence', 0.95)})."
        elif event_type == "PROMPT_EXECUTED":
            return f"LLM execution using model {payload.get('llm', 'LLM')} (Template {payload.get('template_version', '')})."
        elif event_type == "ASSESSMENT_SCORED":
            return f"Composite score computed: {payload.get('composite_score', 0.0)} points via policy {payload.get('policy', '')}."
        elif event_type == "EXPERT_REVIEW":
            return f"Review decision '{payload.get('review_status', '')}' submitted by {payload.get('reviewer', 'expert')}."
        return f"Stage {event_type} completed successfully."
