import time
from collections import defaultdict, deque


WINDOW_SECONDS = 60
MAX_REQUESTS = 5

_requests: dict[str, deque[float]] = defaultdict(deque)


def check_rate_limit(key: str) -> bool:
    now = time.monotonic()
    timestamps = _requests[key]

    while timestamps and now - timestamps[0] > WINDOW_SECONDS:
        timestamps.popleft()

    if len(timestamps) >= MAX_REQUESTS:
        return False

    timestamps.append(now)
    return True