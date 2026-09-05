from datetime import datetime, timezone
from typing import Optional
from app.domain.exceptions.execution_exceptions import ExecutionTimeout, TimerFailure


class TimerManager:
    """Manages active timers, grace periods, remaining time, and timeout detection for assessment items."""

    def __init__(self, max_seconds: float = 120.0, grace_period_seconds: float = 5.0):
        self.max_seconds = max_seconds
        self.grace_period_seconds = grace_period_seconds
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.elapsed_pause_seconds: float = 0.0
        self.pause_start_time: Optional[datetime] = None
        self.is_running: bool = False

    def start_timer(self):
        self.start_time = datetime.now(timezone.utc)
        self.is_running = True
        self.elapsed_pause_seconds = 0.0

    def pause_timer(self):
        if self.is_running and not self.pause_start_time:
            self.pause_start_time = datetime.now(timezone.utc)

    def resume_timer(self):
        if self.pause_start_time:
            pause_duration = (datetime.now(timezone.utc) - self.pause_start_time).total_seconds()
            self.elapsed_pause_seconds += pause_duration
            self.pause_start_time = None

    def stop_timer(self) -> float:
        if not self.start_time:
            raise TimerFailure("GLOBAL", "Timer was never started.")
        self.end_time = datetime.now(timezone.utc)
        self.is_running = False
        return self.get_elapsed_seconds()

    def get_elapsed_seconds(self) -> float:
        if not self.start_time:
            return 0.0
        ref_time = self.end_time or datetime.now(timezone.utc)
        raw_elapsed = (ref_time - self.start_time).total_seconds()
        return max(0.0, raw_elapsed - self.elapsed_pause_seconds)

    def get_remaining_seconds(self) -> float:
        elapsed = self.get_elapsed_seconds()
        return max(0.0, (self.max_seconds + self.grace_period_seconds) - elapsed)

    def check_timeout(self, item_id: str):
        elapsed = self.get_elapsed_seconds()
        effective_limit = self.max_seconds + self.grace_period_seconds
        if elapsed > effective_limit:
            raise ExecutionTimeout(item_id, elapsed, self.max_seconds)
