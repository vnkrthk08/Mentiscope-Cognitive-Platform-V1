"""TraceNode Entity."""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional
import uuid


@dataclass
class TraceNode:
    """DAG Node representing a discrete pipeline step, decision, model, or report artifact."""

    node_id: str
    node_type: str  # ASSESSMENT, AUDIO, SPEECH, TRANSCRIPT, PROMPT, EVIDENCE, CONSTRUCT, SCORE, REPORT, RESEARCH_DATASET, EXPERT_REVIEW, EXPERIMENT_COMPARISON
    label: str
    stage: str
    status: str = "COMPLETED"
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "label": self.label,
            "stage": self.stage,
            "status": self.status,
            "details": self.details,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
