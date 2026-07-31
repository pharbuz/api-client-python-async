import json
from typing import Any
from unittest import mock

from dynatrace import DynatraceAsync
from dynatrace.account.reference_data import (
    Permission,
    ReferenceDataService,
    Region,
    TimeZone,
)
from dynatrace.http_client import HttpClient


class MockResponse:
    def __init__(self, json_data: Any = None) -> None:
        self._json_data = json_data
        self.headers: dict[str, str] = {}
        self.text = json.dumps(json_data) if json_data is not None else ""
        self.status_code = 200

    def json(self) -> Any:
        return self._json_data


async def test_reference_data_service_is_exposed(dt: DynatraceAsync) -> None:
    assert isinstance(dt.account.reference_data, ReferenceDataService)


async def test_reference_data_lists_expected_models(dt: DynatraceAsync) -> None:
    async def fake_make_request(
        self: Any,
        path: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        method: str = "GET",
        data: Any = None,
        files: Any = None,
        query_params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> MockResponse:
        if (method, path) == ("GET", "/ref/v1/time-zones"):
            return MockResponse(
                [
                    {
                        "displayName": "(UTC+01:00) Amsterdam, Berlin, Bern",
                        "name": "Europe/Berlin",
                    }
                ]
            )

        if (method, path) == ("GET", "/ref/v1/regions"):
            return MockResponse([{"name": "US East"}])

        if (method, path) == ("GET", "/ref/v1/account/permissions"):
            return MockResponse(
                [
                    {
                        "id": "account-viewer",
                        "description": "View account information",
                    }
                ]
            )

        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        time_zones = await dt.account.reference_data.list_time_zones()
        regions = await dt.account.reference_data.list_regions()
        permissions = await dt.account.reference_data.list_account_permissions()

    assert len(time_zones) == 1
    assert isinstance(time_zones[0], TimeZone)
    assert time_zones[0].display_name == "(UTC+01:00) Amsterdam, Berlin, Bern"
    assert time_zones[0].name == "Europe/Berlin"
    assert len(regions) == 1
    assert isinstance(regions[0], Region)
    assert regions[0].name == "US East"
    assert len(permissions) == 1
    assert isinstance(permissions[0], Permission)
    assert permissions[0].id == "account-viewer"
    assert permissions[0].description == "View account information"
