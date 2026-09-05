class OrchestratorError(Exception):
    """Base domain exception for all Assessment Orchestrator errors."""

    pass


class IllegalStateTransitionError(OrchestratorError):
    """Raised when an illegal FSM stage transition is attempted."""

    def __init__(self, current_stage: str, target_stage: str, session_id: str):
        self.current_stage = current_stage
        self.target_stage = target_stage
        self.session_id = session_id
        super().__init__(
            f"Illegal state transition invariant violation for session '{session_id}': "
            f"Cannot transition from '{current_stage}' to '{target_stage}'."
        )


class InvalidSessionStateError(OrchestratorError):
    """Raised when an operation is performed on a session in an invalid state (e.g. PAUSED, COMPLETED)."""

    def __init__(self, session_id: str, status: str, action: str):
        self.session_id = session_id
        self.status = status
        self.action = action
        super().__init__(
            f"Cannot perform action '{action}' on session '{session_id}' in state '{status}'."
        )


class SessionTimeoutError(OrchestratorError):
    """Raised when an assessment session exceeds its maximum permitted duration or inactivity timeout."""

    def __init__(self, session_id: str, elapsed_seconds: float, max_seconds: float):
        self.session_id = session_id
        self.elapsed_seconds = elapsed_seconds
        self.max_seconds = max_seconds
        super().__init__(
            f"Assessment session '{session_id}' timed out after {elapsed_seconds:.1f}s (max allowed: {max_seconds:.1f}s)."
        )
