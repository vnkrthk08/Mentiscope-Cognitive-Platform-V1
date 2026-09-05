"""TraceEdge Entity."""
from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import uuid


@dataclass
class TraceEdge:
    """DAG Edge representing causal lineage between two TraceNodes."""

    source_node_id: str
    target_node_id: str
    relation_type: str  # TRANSCRIPTS_AUDIO, EXTRACTS_EVIDENCE, EVALUATES_CONSTRUCT, SCORES_ASSESSMENT, REVIEWS_DATASET, COMPARES_EXPERIMENT
    description: str = ""
    edge_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "edge_id": self.edge_id,
            "source_node_id": self.source_node_id,
            "target_node_id": self.target_node_id,
            "relation_type": self.relation_type,
            "description": self.description,
        }
