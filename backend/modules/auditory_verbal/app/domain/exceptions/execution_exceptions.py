class AEEException(Exception):
    """Base exception for Assessment Execution Engine errors."""

    pass


class ExecutionFailure(AEEException):
    def __init__(self, stage: str, reason: str):
        self.stage = stage
        self.reason = reason
        super().__init__(f"Execution failed at stage '{stage}': {reason}")


class ExecutionTimeout(AEEException):
    def __init__(self, item_id: str, elapsed_sec: float, max_sec: float):
        self.item_id = item_id
        self.elapsed_sec = elapsed_sec
        self.max_sec = max_sec
        super().__init__(f"Execution timeout for item '{item_id}': elapsed {elapsed_sec:.1f}s exceeded limit of {max_sec:.1f}s.")


class InvalidExecutionState(AEEException):
    def __init__(self, current_state: str, action: str):
        self.current_state = current_state
        self.action = action
        super().__init__(f"Cannot perform action '{action}' in execution state '{current_state}'.")


class ReplayLimitExceeded(AEEException):
    def __init__(self, item_id: str, max_replays: int):
        self.item_id = item_id
        self.max_replays = max_replays
        super().__init__(f"Replay limit exceeded for item '{item_id}'. Max allowed: {max_replays}.")


class CheckpointFailure(AEEException):
    def __init__(self, session_id: str, reason: str):
        self.session_id = session_id
        super().__init__(f"Checkpoint failure for session '{session_id}': {reason}")


class TimerFailure(AEEException):
    def __init__(self, timer_id: str, reason: str):
        super().__init__(f"Timer error for '{timer_id}': {reason}")


class ProgressCorruption(AEEException):
    def __init__(self, current_index: int, total_items: int):
        super().__init__(f"Progress index corruption: index {current_index} out of total {total_items}.")


class ContextValidationError(AEEException):
    def __init__(self, missing_field: str):
        super().__init__(f"Execution context validation error: missing '{missing_field}'.")
