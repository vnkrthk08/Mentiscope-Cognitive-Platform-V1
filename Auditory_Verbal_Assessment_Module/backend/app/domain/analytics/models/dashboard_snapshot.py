"""Dashboard Snapshot Domain Model."""
from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.domain.analytics.models.assessment_analytics import AssessmentAnalytics
from app.domain.analytics.models.framework_analytics import FrameworkAnalytics
from app.domain.analytics.models.evidence_analytics import EvidenceAnalytics
from app.domain.analytics.models.research_analytics import ResearchAnalytics
from app.domain.analytics.models.platform_analytics import PlatformAnalytics


@dataclass
class DashboardSnapshot:
    snapshot_id: str
    time_window: str
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    assessments: AssessmentAnalytics = field(default_factory=AssessmentAnalytics)
    frameworks: FrameworkAnalytics = field(default_factory=FrameworkAnalytics)
    evidence: EvidenceAnalytics = field(default_factory=EvidenceAnalytics)
    research: ResearchAnalytics = field(default_factory=ResearchAnalytics)
    platform: PlatformAnalytics = field(default_factory=PlatformAnalytics)
