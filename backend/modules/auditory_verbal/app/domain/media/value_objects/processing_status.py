from enum import Enum


class ProcessingStatus(str, Enum):
    UPLOADING = "UPLOADING"
    UPLOADED = "UPLOADED"
    VALIDATING = "VALIDATING"
    VALIDATED = "VALIDATED"
    QUARANTINED = "QUARANTINED"
    QUEUED = "QUEUED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    DELETED = "DELETED"


# Allowed state transitions mapping
ALLOWED_TRANSITIONS = {
    ProcessingStatus.UPLOADING: {ProcessingStatus.UPLOADED, ProcessingStatus.FAILED},
    ProcessingStatus.UPLOADED: {ProcessingStatus.VALIDATING, ProcessingStatus.FAILED},
    ProcessingStatus.VALIDATING: {ProcessingStatus.VALIDATED, ProcessingStatus.QUARANTINED, ProcessingStatus.FAILED},
    ProcessingStatus.VALIDATED: {ProcessingStatus.QUEUED, ProcessingStatus.FAILED},
    ProcessingStatus.QUARANTINED: {ProcessingStatus.DELETED},
    ProcessingStatus.QUEUED: {ProcessingStatus.PROCESSING, ProcessingStatus.FAILED},
    ProcessingStatus.PROCESSING: {ProcessingStatus.COMPLETED, ProcessingStatus.FAILED},
    ProcessingStatus.COMPLETED: {ProcessingStatus.DELETED},
    ProcessingStatus.FAILED: {ProcessingStatus.DELETED},
    ProcessingStatus.DELETED: set(),
}


def can_transition(current: ProcessingStatus, target: ProcessingStatus) -> bool:
    """Verifies if state transition complies with AudioAsset aggregate invariants."""
    return target in ALLOWED_TRANSITIONS.get(current, set())
