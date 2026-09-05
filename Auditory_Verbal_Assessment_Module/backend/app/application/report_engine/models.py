from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import uuid


@dataclass(frozen=True)
class CandidateReport:
    """Simplified presentation view designed for candidates."""

    candidate_summary: str
    decision_band: str
    top_strengths: List[str]
    growth_areas: List[str]


@dataclass(frozen=True)
class CounselorReport:
    """Detailed clinical/counselor presentation view."""

    decision_explanation: str
    construct_narratives: Dict[str, str]
    behavioral_evidence_references: List[str]
    reliability_notes: str


@dataclass(frozen=True)
class ResearchReport:
    """Comprehensive psychometric & provenance audit view for researchers."""

    pipeline_version: str
    calibration_version: str
    prompt_versions: Dict[str, str]
    model_versions: Dict[str, str]
    provenance_map: Dict[str, Any]
    reliability_statistics: Dict[str, Any]


@dataclass(frozen=True)
class AdministratorReport:
    """Operational & audit view for platform administrators."""

    session_id: str
    scenario_id: str
    status: str
    completion_timestamp: str
    audit_hash: str


@dataclass(frozen=True)
class AssessmentReport:
    """Canonical Aggregate Root representing a complete, explainable assessment report."""

    report_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    scenario_id: str = ""
    executive_summary: str = ""
    decision_band: str = "HIGH_COMPETENCY"
    construct_sections: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    score_tables: Dict[str, Any] = field(default_factory=dict)
    reliability_section: Dict[str, Any] = field(default_factory=dict)
    evidence_traceability_map: List[Dict[str, Any]] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    development_areas: List[str] = field(default_factory=list)
    version_metadata: Dict[str, str] = field(default_factory=dict)
    explainability_metadata: Dict[str, Any] = field(default_factory=dict)
    candidate_view: Optional[CandidateReport] = None
    counselor_view: Optional[CounselorReport] = None
    research_view: Optional[ResearchReport] = None
    administrator_view: Optional[AdministratorReport] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
