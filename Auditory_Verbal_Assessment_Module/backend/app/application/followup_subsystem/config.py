"""
Configuration constants for the Adaptive Follow-up Planning Subsystem.
"""

# Construct Coverage Thresholds
MISSING_THRESHOLD: float = 0.2
WEAK_THRESHOLD: float = 0.6

# Coverage Status Categories
STATUS_MISSING: str = "missing"
STATUS_WEAK: str = "weak"
STATUS_SUFFICIENT: str = "sufficient"

# Evidence Scoring Increment
EVIDENCE_CONFIDENCE_INCREMENT: float = 0.25
MAX_CONSTRUCT_CONFIDENCE: float = 1.0
