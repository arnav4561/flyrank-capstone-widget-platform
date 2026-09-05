from __future__ import annotations

import ipaddress
import os
from typing import Any

import requests


class GeoService:
    def lookup(self, ip_address: str | None) -> dict[str, str | None]:
        if not ip_address:
            return self._empty_result()

        try:
            ipaddress.ip_address(ip_address)
        except ValueError:
            return self._empty_result()

        mock_mode = os.getenv("GEO_MOCK_MODE", "false").lower() == "true"

        if mock_mode:
            result = self._mock_provider_a(ip_address)

            if result is not None:
                return result

            result = self._mock_provider_b(ip_address)

            if result is not None:
                return result

            return self._empty_result()

        result = self._provider_a(ip_address)

        if result is not None:
            return result

        result = self._provider_b(ip_address)

        if result is not None:
            return result

        return self._empty_result()

    def _provider_a(
        self,
        ip_address: str,
    ) -> dict[str, str | None] | None:
        try:
            response = requests.get(
                f"http://ip-api.com/json/{ip_address}",
                params={"fields": "status,country,city"},
                timeout=2,
            )

            if response.status_code != 200:
                return None

            data: dict[str, Any] = response.json()

            if data.get("status") != "success":
                return None

            return {
                "country": data.get("country"),
                "city": data.get("city"),
            }

        except (requests.RequestException, ValueError):
            return None

    def _provider_b(
        self,
        ip_address: str,
    ) -> dict[str, str | None] | None:
        try:
            response = requests.get(
                f"https://ipapi.co/{ip_address}/json/",
                timeout=2,
            )

            if response.status_code != 200:
                return None

            data: dict[str, Any] = response.json()

            if data.get("error"):
                return None

            return {
                "country": data.get("country_name"),
                "city": data.get("city"),
            }

        except (requests.RequestException, ValueError):
            return None

    def _mock_provider_a(
        self,
        ip_address: str,
    ) -> dict[str, str | None] | None:
        if ip_address == "203.0.113.10":
            return {
                "country": "Mockland",
                "city": "Provider A City",
            }

        return None

    def _mock_provider_b(
        self,
        ip_address: str,
    ) -> dict[str, str | None] | None:
        if ip_address == "203.0.113.20":
            return {
                "country": "Mockland",
                "city": "Provider B City",
            }

        return None

    @staticmethod
    def _empty_result() -> dict[str, str | None]:
        return {
            "country": None,
            "city": None,
        }