"""Fixed-step simulation timing for the interactive loops."""

from collections import deque
from time import perf_counter_ns, sleep

SIMULATION_HZ = 60
STEP_SECONDS = 1 / SIMULATION_HZ
NANOSECONDS_PER_SECOND = 1_000_000_000


class FixedStepClock:
    def __init__(self):
        self.remainder = 0

    def advance(self, elapsed_ns):
        # Limit catch-up after a long stall, such as dragging the window.
        elapsed_ns = min(elapsed_ns, NANOSECONDS_PER_SECOND // 4)
        steps, self.remainder = divmod(
            self.remainder + elapsed_ns * SIMULATION_HZ, NANOSECONDS_PER_SECOND
        )
        return steps


class RenderClock:
    """Pace rendered frames and measure their wall-clock rate."""

    def __init__(self):
        self.timestamps = deque([perf_counter_ns()], maxlen=11)

    def tick(self, fps):
        previous = self.timestamps[-1]
        now = perf_counter_ns()
        if fps:
            interval = (NANOSECONDS_PER_SECOND + fps - 1) // fps
            remaining = previous + interval - now
            if remaining > 0:
                sleep(remaining / NANOSECONDS_PER_SECOND)
                now = perf_counter_ns()
        self.timestamps.append(now)
        return now - previous

    @property
    def fps(self):
        duration = self.timestamps[-1] - self.timestamps[0]
        if duration == 0:
            return 0.0
        return (len(self.timestamps) - 1) * NANOSECONDS_PER_SECOND / duration
