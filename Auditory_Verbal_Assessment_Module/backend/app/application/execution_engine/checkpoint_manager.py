from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import uuid
from app.domain.exceptions.execution_exceptions import CheckpointFailure


@dataclass
class ExecutionSnapshot:
    """Immutable snapshot of runtime execution state for checkpointing."""

    checkpoint_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str = ""
    stage: str = ""
    current_item_index: int = 0
    fsm_state: str = "READY"
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class CheckpointManager:
    """Manages runtime state snapshots for browser crash recovery and crash checkpointing."""

    def __init__(self):
        self._checkpoints: Dict[str, List[ExecutionSnapshot]] = {}

    def create_checkpoint(
        self, session_id: str, stage: str, item_index: int, fsm_state: str, metadata: Optional[Dict[str, Any]] = None
    ) -> ExecutionSnapshot:
        snapshot = ExecutionSnapshot(
            session_id=session_id,
            stage=stage,
            current_item_index=item_index,
            fsm_state=fsm_state,
            metadata=metadata or {},
        )
        if session_id not in self._checkpoints:
            self._checkpoints[session_id] = []
        self._checkpoints[session_id].append(snapshot)
        return snapshot

    def get_latest_checkpoint(self, session_id: str) -> Optional[ExecutionSnapshot]:
        snapshots = self._checkpoints.get(session_id, [])
        return snapshots[-1] if snapshots else None

    def restore_checkpoint(self, session_id: str) -> ExecutionSnapshot:
        latest = self.get_latest_checkpoint(session_id)
        if not latest:
            raise CheckpointFailure(session_id, "No valid checkpoint snapshot found for session.")
        return latest
