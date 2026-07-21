import json
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
    def __init__(self, json_data=None):
        self._json_data = json_data
        self.headers = {}
        self.text = json.dumps(json_data) if json_data is not None else ""
        self.status_code = 200

    def json(self):
        return self._json_data


async def test_reference_data_service_is_exposed(dt: DynatraceAsync):
    assert isinstance(dt.account.reference_data, ReferenceDataService)


async def test_reference_data_lists_expected_models(dt: DynatraceAsync):
    async def fake_make_request(
        self,
        path,
        params=None,
        headers=None,
        method="GET",
        data=None,
        files=None,
        query_params=None,
        **kwargs,
    ):
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
