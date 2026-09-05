from enum import Enum


class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


# API Constants
API_V1_STR = "/api/v1"
PROJECT_NAME = "MentiScope Cognitive & Psychological Assessment Platform"
PROJECT_VERSION = "1.0.0"

# Header Constants
HEADER_REQUEST_ID = "X-Request-ID"
HEADER_CORRELATION_ID = "X-Correlation-ID"
HEADER_PROCESS_TIME = "X-Process-Time"

# Security Constants
ALGORITHM_HS256 = "HS256"
DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours
