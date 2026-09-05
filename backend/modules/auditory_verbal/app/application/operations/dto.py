"""
POSRP DTO Schemas (Pydantic v2).
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Health DTOs
# ---------------------------------------------------------------------------


class ServiceHealthResponse(BaseModel):
    service_name: str
    status: str
    latency_ms: float
    last_checked: str
    details: Dict[str, Any] = Field(default_factory=dict)


class HealthCheckResponse(BaseModel):
    check_id: str
    overall_status: str
    system_status: Dict[str, Any]
    services: List[ServiceHealthResponse]
    healthy_count: int
    degraded_count: int
    unavailable_count: int
    checked_at: str


# ---------------------------------------------------------------------------
# Platform Status DTOs
# ---------------------------------------------------------------------------


class PlatformStatusResponse(BaseModel):
    environment: str
    version: str
    uptime_seconds: float
    total_assessments: int
    total_reports: int
    total_research_datasets: int
    registered_models: int
    audit_sessions: int
    system_status: Dict[str, Any]
    generated_at: str


# ---------------------------------------------------------------------------
# Metrics DTOs
# ---------------------------------------------------------------------------


class CapacitySnapshotResponse(BaseModel):
    snapshot_id: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    db_connections_active: int
    db_connections_max: int
    db_utilization_percent: float
    api_requests_per_minute: float
    avg_api_latency_ms: float
    pipeline_throughput_per_hour: float
    assessment_completion_rate: float
    error_rate_percent: float
    captured_at: str


class OperationalMetricsResponse(BaseModel):
    capacity: CapacitySnapshotResponse
    database_latency_ms: float
    redis_latency_ms: float
    active_alert_count: int
    recent_backup_count: int
    generated_at: str


# ---------------------------------------------------------------------------
# Configuration DTOs
# ---------------------------------------------------------------------------


class ConfigurationProfileResponse(BaseModel):
    profile_id: str
    profile_name: str
    created_by: str
    config_data: Dict[str, Any]
    version: int
    is_active: bool
    config_hash: str
    description: str
    created_at: str


class ConfigurationListResponse(BaseModel):
    profiles: List[ConfigurationProfileResponse]
    total: int


# ---------------------------------------------------------------------------
# Backup & Restore DTOs
# ---------------------------------------------------------------------------


class BackupJobRequest(BaseModel):
    backup_type: str = Field(..., description="DATABASE | RESEARCH_DATA | AUDIT_ARCHIVE | CONFIGURATION")
    initiated_by: str = Field(default="system")


class BackupJobResponse(BaseModel):
    job_id: str
    backup_type: str
    initiated_by: str
    status: str
    target_path: str
    size_bytes: int
    checksum: str
    error_message: str
    started_at: str
    completed_at: Optional[str]


class RestoreJobRequest(BaseModel):
    backup_job_id: str
    restore_type: str = Field(..., description="DATABASE | RESEARCH_DATA | AUDIT_ARCHIVE | CONFIGURATION")
    initiated_by: str = Field(default="system")
    simulate_first: bool = Field(default=True)


class RestoreJobResponse(BaseModel):
    job_id: str
    backup_job_id: str
    restore_type: str
    initiated_by: str
    status: str
    simulation_result: str
    error_message: str
    started_at: str
    completed_at: Optional[str]


# ---------------------------------------------------------------------------
# Alert DTOs
# ---------------------------------------------------------------------------


class AlertRuleResponse(BaseModel):
    rule_id: str
    rule_name: str
    metric_name: str
    condition: str
    threshold: float
    severity: str
    is_enabled: bool
    cooldown_seconds: int
    created_at: str


class AlertEventResponse(BaseModel):
    event_id: str
    rule_id: str
    rule_name: str
    metric_name: str
    metric_value: float
    threshold: float
    severity: str
    status: str
    resolution_note: str
    triggered_at: str
    resolved_at: Optional[str]


class AlertsResponse(BaseModel):
    rules: List[AlertRuleResponse]
    active_events: List[AlertEventResponse]
    total_rules: int
    total_active_events: int
