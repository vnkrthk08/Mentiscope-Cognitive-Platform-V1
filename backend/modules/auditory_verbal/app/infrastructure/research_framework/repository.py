from typing import Dict, List, Optional
from app.infrastructure.research_framework.models import ResearchDashboardModel


class AnalyticsRepository:
    """In-memory persistence abstraction storing research dashboard snapshots and historical trends."""

    def __init__(self):
        self._snapshots: Dict[str, ResearchDashboardModel] = {}

    def save_snapshot(self, model: ResearchDashboardModel):
        self._snapshots[model.snapshot_id] = model

    def get_snapshot(self, snapshot_id: str) -> Optional[ResearchDashboardModel]:
        return self._snapshots.get(snapshot_id)

    def list_snapshots(self) -> List[ResearchDashboardModel]:
        return list(self._snapshots.values())
