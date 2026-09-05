from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from app.domain.entities.assessment_session import AssessmentSession
from app.domain.entities.scenario import Scenario
from app.application.execution_engine.state_machine import ExecutionStateMachine
from app.application.execution_engine.timer_manager import TimerManager
from app.application.execution_engine.replay_manager import ReplayManager
from app.application.execution_engine.progress_tracker import ProgressTracker
from app.domain.exceptions.execution_exceptions import ContextValidationError


@dataclass
class ExecutionContext:
    """Runtime Execution Context container passed to stage executors."""

    session: AssessmentSession
    scenario: Scenario
    current_stage: str
    fsm: ExecutionStateMachine = field(default_factory=ExecutionStateMachine)
    timer_manager: TimerManager = field(default_factory=TimerManager)
    replay_manager: ReplayManager = field(default_factory=ReplayManager)
    progress_tracker: ProgressTracker = field(default_factory=ProgressTracker)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.session:
            raise ContextValidationError("session")
        if not self.scenario:
            raise ContextValidationError("scenario")
        if not self.current_stage:
            raise ContextValidationError("current_stage")
