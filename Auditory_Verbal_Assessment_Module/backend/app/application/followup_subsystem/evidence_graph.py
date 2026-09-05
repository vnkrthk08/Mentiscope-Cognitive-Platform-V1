"""
Module: Behavioral Evidence Graph Subsystem.
Models candidate responses as an interconnected network of typed nodes and directed edges.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


class NodeType(str, Enum):
    CONSTRUCT = "CONSTRUCT"
    EVIDENCE = "EVIDENCE"
    CLAIM = "CLAIM"
    DECISION = "DECISION"
    STAKEHOLDER = "STAKEHOLDER"
    RISK = "RISK"
    REASONING = "REASONING"
    CONTRADICTION = "CONTRADICTION"
    ACTION = "ACTION"


class EdgeType(str, Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    EXPLAINS = "explains"
    DEPENDS_ON = "depends_on"
    EXTENDS = "extends"
    REVISES = "revises"
    REFERENCES = "references"


@dataclass
class GraphNode:
    id: str
    node_type: NodeType
    label: str
    content: str
    turn_number: int
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "node_type": self.node_type.value,
            "label": self.label,
            "content": self.content,
            "turn_number": self.turn_number,
            "confidence": self.confidence,
            "metadata": self.metadata,
        }


@dataclass
class GraphEdge:
    source_id: str
    target_id: str
    edge_type: EdgeType
    weight: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "edge_type": self.edge_type.value,
            "weight": self.weight,
        }


class BehavioralEvidenceGraph:
    """Graph structure modeling interview evidence, construct links, claims, and contradictions."""

    def __init__(self, session_id: str = "default_session"):
        self.session_id = session_id
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []

    def add_node(self, node: GraphNode):
        if node.id not in self.nodes:
            self.nodes[node.id] = node

    def add_edge(self, edge: GraphEdge):
        self.edges.append(edge)

    def get_nodes_by_type(self, node_type: NodeType) -> List[GraphNode]:
        return [n for n in self.nodes.values() if n.node_type == node_type]

    def get_edges_by_type(self, edge_type: EdgeType) -> List[GraphEdge]:
        return [e for e in self.edges if e.edge_type == edge_type]

    def calculate_diversity_score(self) -> float:
        """Calculates normalized node type diversity (0.0 to 1.0)."""
        observed_types = {n.node_type for n in self.nodes.values()}
        return round(len(observed_types) / len(NodeType), 2)

    def get_contradiction_count(self) -> int:
        return len(self.get_edges_by_type(EdgeType.CONTRADICTS))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges],
            "node_count": len(self.nodes),
            "edge_count": len(self.edges),
            "diversity_score": self.calculate_diversity_score(),
            "contradiction_count": self.get_contradiction_count(),
        }
