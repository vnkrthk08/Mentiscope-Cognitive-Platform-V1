from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.persistence.database.session import AsyncSessionLocal
from app.infrastructure.persistence.repositories import (
    AssessmentRepository,
    ScenarioRepository,
    TranscriptRepository,
    EvidenceRepository,
    ConstructRepository,
    ScoringRepository,
    ReportRepository,
    ResearchRepository,
    PromptRepository,
    PlatformEventRepository,
)


class UnitOfWork:
    """Async Unit of Work pattern managing database session lifetime and transaction boundaries."""

    def __init__(self, session_factory=AsyncSessionLocal):
        self.session_factory = session_factory
        self.session: Optional[AsyncSession] = None

    async def __aenter__(self):
        self.session = self.session_factory()
        self.assessments = AssessmentRepository(self.session)
        self.scenarios = ScenarioRepository(self.session)
        self.transcripts = TranscriptRepository(self.session)
        self.evidences = EvidenceRepository(self.session)
        self.constructs = ConstructRepository(self.session)
        self.scores = ScoringRepository(self.session)
        self.reports = ReportRepository(self.session)
        self.research = ResearchRepository(self.session)
        self.prompts = PromptRepository(self.session)
        self.events = PlatformEventRepository(self.session)

        # Identity S4 repositories
        from app.infrastructure.identity.repositories import (
            UserRepository,
            RoleRepository,
            PermissionRepository,
            TokenRepository,
            SessionRepository,
            AuditLogRepository,
        )
        self.users = UserRepository(self.session)
        self.roles = RoleRepository(self.session)
        self.permissions = PermissionRepository(self.session)
        self.tokens = TokenRepository(self.session)
        self.user_sessions = SessionRepository(self.session)
        self.audit_logs = AuditLogRepository(self.session)

        # Media S5 repositories
        from app.infrastructure.media.repositories import AudioRepository
        self.audio_assets = AudioRepository(self.session)

        # Speech S6 repositories
        from app.infrastructure.speech.repositories import SpeechRepository, TranscriptionJobRepository
        self.speech_transcripts = SpeechRepository(self.session)
        self.transcription_jobs = TranscriptionJobRepository(self.session)

        # Prompt S7 repositories
        from app.infrastructure.prompt.repositories import PromptRepository as LLMPromptRepository
        self.llm_prompts = LLMPromptRepository(self.session)

        # Behavior S8 repositories
        from app.infrastructure.behavior.repositories import BehaviorRepository
        self.behavior_evidences = BehaviorRepository(self.session)

        # Construct S9 repositories
        from app.infrastructure.construct.repositories import ConstructRepository as CEEConstructRepository
        self.construct_evaluations = CEEConstructRepository(self.session)

        # Assessment S10 repositories
        from app.infrastructure.assessment.repositories import AssessmentReportRepository as ASRAssessmentReportRepository
        self.assessment_reports = ASRAssessmentReportRepository(self.session)

        # PVCSF: Psychometric Validation & Calibration Support Framework repositories
        from app.infrastructure.research.repositories import (
            ValidationDatasetRepository,
            ExpertReviewRepository,
            CalibrationBatchRepository,
            ResearchExportRepository,
        )
        self.validation_datasets = ValidationDatasetRepository(self.session)
        self.expert_reviews = ExpertReviewRepository(self.session)
        self.calibration_batches = CalibrationBatchRepository(self.session)
        self.research_exports = ResearchExportRepository(self.session)

        # RAIP Phase 12 Analytics repository
        from app.infrastructure.analytics.repository import AnalyticsRepository
        self.analytics = AnalyticsRepository(self.session)

        # MGEP Phase 13 Governance repositories
        from app.infrastructure.governance.repositories import (
            ModelRegistryRepository,
            ConfigurationSnapshotRepository,
            ExperimentRepository,
            ExperimentRunRepository,
            ComparisonReportRepository,
        )
        self.model_registry = ModelRegistryRepository(self.session)
        self.config_snapshots = ConfigurationSnapshotRepository(self.session)
        self.experiments = ExperimentRepository(self.session)
        self.experiment_runs = ExperimentRunRepository(self.session)
        self.comparison_reports = ComparisonReportRepository(self.session)

        # ACTP Phase 14 Audit, Compliance & Traceability repositories
        from app.infrastructure.actp.repositories import (
            AuditSessionRepository,
            AuditEventRepository,
            DecisionRecordRepository,
        )
        self.audit_sessions = AuditSessionRepository(self.session)
        self.audit_events = AuditEventRepository(self.session)
        self.decision_records = DecisionRecordRepository(self.session)

        # POSRP Phase 15 Operations repositories
        from app.infrastructure.operations.repositories import (
            ConfigurationProfileRepository,
            BackupJobRepository,
            RestoreJobRepository,
            AlertRuleRepository,
            AlertEventRepository,
        )
        self.config_profiles = ConfigurationProfileRepository(self.session)
        self.backup_jobs = BackupJobRepository(self.session)
        self.restore_jobs = RestoreJobRepository(self.session)
        self.alert_rules = AlertRuleRepository(self.session)
        self.alert_events = AlertEventRepository(self.session)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            try:
                if exc_type:
                    await self.rollback()
                else:
                    await self.commit()
            finally:
                await self.session.close()
                self.session = None

    async def commit(self):
        if self.session:
            await self.session.commit()

    async def rollback(self):
        if self.session:
            await self.session.rollback()
pre=1.0
