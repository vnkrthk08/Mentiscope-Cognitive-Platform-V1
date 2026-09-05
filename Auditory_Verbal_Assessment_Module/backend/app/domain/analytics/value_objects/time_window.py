"""TimeWindow Value Object for Analytics querying."""
from enum import Enum


class TimeWindow(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ALL_TIME = "all_time"
