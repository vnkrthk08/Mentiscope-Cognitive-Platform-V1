from typing import Dict, List
from app.domain.exceptions.execution_exceptions import InvalidExecutionState
from app.core.logging import logger

VALID_EXECUTION_TRANSITIONS: Dict[str, List[str]] = {
    "READY": ["RUNNING", "CANCELLED", "FAILED"],
    "RUNNING": ["WAITING_FOR_RESPONSE", "PROCESSING", "COMPLETED", "PAUSED", "TIMED_OUT", "CANCELLED", "FAILED"],
    "WAITING_FOR_RESPONSE": ["PROCESSING", "RUNNING", "PAUSED", "TIMED_OUT", "CANCELLED", "FAILED"],
    "PROCESSING": ["RUNNING", "COMPLETED", "PAUSED", "FAILED"],
    "PAUSED": ["RUNNING", "WAITING_FOR_RESPONSE", "CANCELLED", "FAILED"],
    "TIMED_OUT": ["FAILED", "RUNNING"],
    "COMPLETED": [],
    "FAILED": [],
    "CANCELLED": [],
}


class ExecutionStateMachine:
    """Controls runtime execution state transitions within an assessment stage."""

    def __init__(self, initial_state: str = "READY"):
        self.current_state = initial_state

    def transition_to(self, target_state: str) -> str:
        allowed = VALID_EXECUTION_TRANSITIONS.get(self.current_state, [])
        if target_state not in allowed:
            logger.error(f"[AEE FSM] Invalid transition: {self.current_state} -> {target_state}")
            raise InvalidExecutionState(self.current_state, target_state)

        logger.info(f"[AEE FSM] Execution State Transition: {self.current_state} -> {target_state}")
        self.current_state = target_state
        return self.current_state
