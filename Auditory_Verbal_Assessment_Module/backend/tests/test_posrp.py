"""
POSRP Test Suite — Platform Operations & Site Reliability Platform (Phase 15).

Tests for:
  - Domain Value Objects (SystemStatus, ServiceHealth)
  - Domain Entities (HealthCheck, ConfigurationProfile, BackupJob, RestoreJob, AlertRule, AlertEvent, MaintenanceWindow, CapacitySnapshot)
  - Application Services (HealthMonitorService, MetricsCollectorService, ConfigurationManagerService, BackupManagerService, AlertManagerService)
  - Infrastructure Repositories (ConfigurationProfileRepository, BackupJobRepository, RestoreJobRepository, AlertRuleRepository, AlertEventRepository)
  - Infrastructure Metrics (POSRPMetrics)
  - API router endpoints (/operations/*)
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.domain.operations.value_objects.system_status import SystemStatus
from app.domain.operations.value_objects.service_health import ServiceHealth
from app.domain.operations.entities.health_check import HealthCheck
from app.domain.operations.entities.configuration_profile import ConfigurationProfile
from app.domain.operations.entities.backup_job import BackupJob
from app.domain.operations.entities.restore_job import RestoreJob
from app.domain.operations.entities.alert_rule import AlertRule
from app.domain.operations.entities.alert_event import AlertEvent
from app.domain.operations.entities.maintenance_window import MaintenanceWindow
from app.domain.operations.entities.capacity_snapshot import CapacitySnapshot


# ---------------------------------------------------------------------------
# 1. Domain Value Object Tests
# ---------------------------------------------------------------------------


class TestPOSRPValueObjects:
    def test_system_status_to_dict(self):
        ss = SystemStatus(status="HEALTHY", cpu_percent=25.0, memory_percent=60.0)
        d = ss.to_dict()
        assert d["status"] == "HEALTHY"
        assert d["cpu_percent"] == 25.0

    def test_service_health_to_dict(self):
        sh = ServiceHealth(service_name="database", status="HEALTHY", latency_ms=1.5)
        d = sh.to_dict()
        assert d["service_name"] == "database"
        assert d["latency_ms"] == 1.5


# ---------------------------------------------------------------------------
# 2. Domain Entity Tests
# ---------------------------------------------------------------------------


class TestPOSRPDomainEntities:
    def test_health_check_aggregation(self):
        ss = SystemStatus(status="HEALTHY")
        services = [
            ServiceHealth(service_name="db", status="HEALTHY"),
            ServiceHealth(service_name="redis", status="HEALTHY"),
        ]
        hc = HealthCheck(system_status=ss, services=services)
        assert hc.overall_status == "HEALTHY"
        assert hc.healthy_count == 2
        assert hc.unavailable_count == 0

    def test_health_check_degraded_when_unavailable(self):
        ss = SystemStatus(status="DEGRADED")
        services = [
            ServiceHealth(service_name="db", status="HEALTHY"),
            ServiceHealth(service_name="redis", status="UNAVAILABLE"),
        ]
        hc = HealthCheck(system_status=ss, services=services)
        assert hc.overall_status == "CRITICAL"
        assert hc.unavailable_count == 1

    def test_configuration_profile_hashing(self):
        cp1 = ConfigurationProfile(profile_name="prod", created_by="admin", config_data={"a": 1})
        cp2 = ConfigurationProfile(profile_name="prod", created_by="admin", config_data={"a": 1})
        assert cp1.config_hash == cp2.config_hash

    def test_backup_job_lifecycle(self):
        bj = BackupJob(backup_type="DATABASE", initiated_by="admin")
        assert bj.status == "PENDING"
        bj.start()
        assert bj.status == "RUNNING"
        bj.complete(target_path="/tmp/backup.json", size_bytes=1024, checksum="abc123hash")
        assert bj.status == "COMPLETED"
        assert bj.checksum == "abc123hash"
        bj.verify()
        assert bj.status == "VERIFIED"

    def test_restore_job_simulation(self):
        rj = RestoreJob(backup_job_id="job-001", restore_type="DATABASE", initiated_by="admin")
        assert rj.status == "PENDING"
        rj.simulate(passed=True)
        assert rj.simulation_result == "PASS"
        rj.start_restore()
        assert rj.status == "RESTORING"
        rj.complete()
        assert rj.status == "COMPLETED"

    def test_alert_rule_evaluation(self):
        rule = AlertRule(rule_name="High Latency", metric_name="latency", condition="GT", threshold=500.0)
        assert rule.evaluate(600.0) is True
        assert rule.evaluate(400.0) is False

    def test_alert_event_resolution(self):
        ae = AlertEvent(
            rule_id="r1", rule_name="Latency", metric_name="latency",
            metric_value=600.0, threshold=500.0, severity="WARNING"
        )
        assert ae.status == "OPEN"
        ae.acknowledge()
        assert ae.status == "ACKNOWLEDGED"
        ae.resolve(note="Scaled cluster")
        assert ae.status == "RESOLVED"
        assert ae.resolved_at is not None

    def test_maintenance_window(self):
        start = datetime.now(timezone.utc)
        end = datetime.now(timezone.utc)
        with pytest.raises(ValueError):
            MaintenanceWindow(title="Invalid", scheduled_by="admin", start_time=end, end_time=start)

    def test_capacity_snapshot_utilization(self):
        cs = CapacitySnapshot(
            cpu_percent=10.0, memory_percent=40.0, disk_percent=50.0,
            db_connections_active=10, db_connections_max=20,
            api_requests_per_minute=100.0, avg_api_latency_ms=20.0,
            pipeline_throughput_per_hour=50.0, assessment_completion_rate=99.0,
            error_rate_percent=0.1
        )
        assert cs.db_utilization_percent == 50.0


# ---------------------------------------------------------------------------
# 3. Database Helper
# ---------------------------------------------------------------------------


async def _make_posrp_session():
    """Creates a fresh in-memory SQLite database with POSRP tables."""
    import app.infrastructure.operations.orm_models
    import app.infrastructure.persistence.models.orm_models
    from app.infrastructure.persistence.database.base import Base

    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    session = factory()
    return engine, session


# ---------------------------------------------------------------------------
# 4. Service & Repository Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_health_monitor_service():
    from app.application.operations.services.health_monitor_service import HealthMonitorService

    engine, session = await _make_posrp_session()
    try:
        hms = HealthMonitorService(session)
        hc = await hms.run_health_check()
        assert hc.overall_status in ("HEALTHY", "DEGRADED", "CRITICAL")
        assert len(hc.services) >= 5
    finally:
        await session.close()
        await engine.dispose()


@pytest.mark.asyncio
async def test_configuration_manager_service():
    from app.application.operations.services.configuration_manager_service import ConfigurationManagerService

    engine, session = await _make_posrp_session()
    try:
        cms = ConfigurationManagerService(session)

        # Get default active profile
        p1 = await cms.get_active_profile("staging")
        await session.commit()
        assert p1.profile_name == "staging"
        assert p1.version == 1

        # Create new versioned profile
        p2 = await cms.create_profile(
            profile_name="staging",
            created_by="devops",
            config_data={"env": "staging", "debug": True},
            description="V2 Profile",
        )
        await session.commit()

        assert p2.version == 2
        assert p2.is_active is True

        # Ensure V1 deactivated
        profiles = await cms.list_profiles("staging")
        assert len(profiles) == 2
    finally:
        await session.close()
        await engine.dispose()


@pytest.mark.asyncio
async def test_backup_and_restore_services():
    from app.application.operations.services.backup_manager_service import BackupManagerService

    engine, session = await _make_posrp_session()
    try:
        bms = BackupManagerService(session)

        # Initiate backup
        b_job = await bms.initiate_backup("DATABASE", "admin")
        await session.commit()

        assert b_job.status == "VERIFIED"
        assert b_job.checksum != ""
        assert os.path.exists(b_job.target_path)

        # Initiate restore
        r_job = await bms.initiate_restore(b_job.job_id, "DATABASE", "admin", simulate_first=True)
        await session.commit()

        assert r_job.status == "COMPLETED"
        assert r_job.simulation_result == "PASS"
    finally:
        await session.close()
        await engine.dispose()


@pytest.mark.asyncio
async def test_alert_manager_service():
    from app.application.operations.services.alert_manager_service import AlertManagerService

    engine, session = await _make_posrp_session()
    try:
        ams = AlertManagerService(session)

        rules = await ams.get_or_create_default_rules()
        await session.commit()
        assert len(rules) >= 5

        # Fire metric that triggers alert rule (api_latency > 500)
        events = await ams.evaluate_metrics("api_latency", 650.0)
        await session.commit()
        assert len(events) == 1
        assert events[0].rule_name == "High API Latency"

        active = await ams.list_active_alerts()
        assert len(active) == 1
    finally:
        await session.close()
        await engine.dispose()


# ---------------------------------------------------------------------------
# 5. API Integration Tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_operations_api_health(async_client):
    res = await async_client.get("/api/v1/operations/health")
    assert res.status_code == 200
    data = res.json()
    assert "overall_status" in data
    assert "services" in data
    assert data["healthy_count"] >= 1


@pytest.mark.asyncio
async def test_operations_api_status(async_client):
    res = await async_client.get("/api/v1/operations/status")
    assert res.status_code == 200
    data = res.json()
    assert "environment" in data
    assert "uptime_seconds" in data
    assert "system_status" in data


@pytest.mark.asyncio
async def test_operations_api_metrics(async_client):
    res = await async_client.get("/api/v1/operations/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "capacity" in data
    assert "database_latency_ms" in data


@pytest.mark.asyncio
async def test_operations_api_configuration(async_client):
    res = await async_client.get("/api/v1/operations/configuration")
    assert res.status_code == 200
    data = res.json()
    assert "profiles" in data
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_operations_api_backup_and_restore(async_client):
    # Initiate backup
    res_b = await async_client.post(
        "/api/v1/operations/backup",
        json={"backup_type": "DATABASE", "initiated_by": "api_test"},
    )
    assert res_b.status_code == 201
    b_data = res_b.json()
    job_id = b_data["job_id"]
    assert b_data["status"] == "VERIFIED"

    # Initiate restore
    res_r = await async_client.post(
        "/api/v1/operations/restore",
        json={
            "backup_job_id": job_id,
            "restore_type": "DATABASE",
            "initiated_by": "api_test",
            "simulate_first": True,
        },
    )
    assert res_r.status_code == 200
    r_data = res_r.json()
    assert r_data["status"] == "COMPLETED"
    assert r_data["simulation_result"] == "PASS"


@pytest.mark.asyncio
async def test_operations_api_alerts(async_client):
    res = await async_client.get("/api/v1/operations/alerts")
    assert res.status_code == 200
    data = res.json()
    assert "rules" in data
    assert data["total_rules"] >= 5
