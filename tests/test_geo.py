import os

from app.services.geo import GeoService


def setup_mock_mode():
    os.environ["GEO_MOCK_MODE"] = "true"


def teardown_mock_mode():
    os.environ.pop("GEO_MOCK_MODE", None)


def test_provider_a_success():
    setup_mock_mode()

    try:
        result = GeoService().lookup("203.0.113.10")

        assert result == {
            "country": "Mockland",
            "city": "Provider A City",
        }
    finally:
        teardown_mock_mode()


def test_provider_a_fails_provider_b_succeeds():
    setup_mock_mode()

    try:
        result = GeoService().lookup("203.0.113.20")

        assert result == {
            "country": "Mockland",
            "city": "Provider B City",
        }
    finally:
        teardown_mock_mode()


def test_both_providers_fail():
    setup_mock_mode()

    try:
        result = GeoService().lookup("203.0.113.30")

        assert result == {
            "country": None,
            "city": None,
        }
    finally:
        teardown_mock_mode()


def test_invalid_ip_returns_empty_result():
    result = GeoService().lookup("not-an-ip")

    assert result == {
        "country": None,
        "city": None,
    }