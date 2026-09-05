"""AlertManagerService — Evaluates threshold rules and manages operational alerts."""
from __future__ import annotations

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.operations.entities.alert_event import AlertEvent
from app.domain.operations.entities.alert_rule import AlertRule


class AlertManagerService:
    """Manages threshold rules, evaluates metrics, triggers alerts, and supports resolution."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_or_create_default_rules(self) -> List[AlertRule]:
        """Seeds default operational alert rules if none registered."""
        from app.infrastructure.operations.repositories import AlertRuleRepository
        repo = AlertRuleRepository(self._session)
        rules = await repo.list_rules()
        if rules:
            return rules

        defaults = [
            AlertRule(rule_name="High API Latency", metric_name="api_latency", condition="GT", threshold=500.0, severity="WARNING"),
            AlertRule(rule_name="High Error Rate", metric_name="error_rate", condition="GT", threshold=5.0, severity="CRITICAL"),
            AlertRule(rule_name="Storage Capacity High", metric_name="storage_capacity", condition="GT", threshold=85.0, severity="WARNING"),
            AlertRule(rule_name="Queue Backlog High", metric_name="queue_backlog", condition="GT", threshold=100.0, severity="WARNING"),
            AlertRule(rule_name="Provider Failure Detected", metric_name="provider_failure", condition="EQ", threshold=1.0, severity="CRITICAL"),
        ]
        for r in defaults:
            await repo.save(r)
        return defaults

    async def evaluate_metrics(self, metric_name: str, metric_value: float) -> List[AlertEvent]:
        """Evaluates a metric against enabled rules and fires alert events if triggered."""
        from app.infrastructure.operations.repositories import AlertEventRepository, AlertRuleRepository
        rule_repo = AlertRuleRepository(self._session)
        event_repo = AlertEventRepository(self._session)

        rules = await rule_repo.list_rules_by_metric(metric_name)
        triggered_events = []

        for rule in rules:
            if rule.evaluate(metric_value):
                event = AlertEvent(
                    rule_id=rule.rule_id,
                    rule_name=rule.rule_name,
                    metric_name=rule.metric_name,
                    metric_value=metric_value,
                    threshold=rule.threshold,
                    severity=rule.severity,
                )
                await event_repo.save(event)
                triggered_events.append(event)

        return triggered_events

    async def list_active_alerts(self) -> List[AlertEvent]:
        from app.infrastructure.operations.repositories import AlertEventRepository
        return await AlertEventRepository(self._session).list_active()

    async def list_rules(self) -> List[AlertRule]:
        from app.infrastructure.operations.repositories import AlertRuleRepository
        return await AlertRuleRepository(self._session).list_rules()
