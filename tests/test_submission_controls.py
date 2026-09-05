import time

from app.core import rate_limit


def test_rate_limit_allows_first_five_requests(monkeypatch):
    rate_limit._requests.clear()

    key = "test-rate-limit"

    for _ in range(5):
        assert rate_limit.check_rate_limit(key) is True

    rate_limit._requests.clear()


def test_rate_limit_blocks_sixth_request(monkeypatch):
    rate_limit._requests.clear()

    key = "test-rate-limit-block"

    for _ in range(5):
        assert rate_limit.check_rate_limit(key) is True

    assert rate_limit.check_rate_limit(key) is False

    rate_limit._requests.clear()


def test_rate_limit_resets_after_window(monkeypatch):
    rate_limit._requests.clear()

    key = "test-rate-limit-window"

    current_time = 1000.0

    monkeypatch.setattr(
        rate_limit.time,
        "monotonic",
        lambda: current_time,
    )

    for _ in range(5):
        assert rate_limit.check_rate_limit(key) is True

    assert rate_limit.check_rate_limit(key) is False

    current_time += rate_limit.WINDOW_SECONDS + 1

    assert rate_limit.check_rate_limit(key) is True

    rate_limit._requests.clear()