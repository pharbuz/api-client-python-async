import json
from unittest import mock

from dynatrace import DynatraceAsync
from dynatrace.account.env_v2.settings import EffectiveSettingsValue, SettingService
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList
from test.async_utils import collect


class MockResponse:
    def __init__(self, json_data=None):
        self._json_data = json_data
        self.headers = {}
        self.text = json.dumps(json_data) if json_data is not None else ""
        self.status_code = 200

    def json(self):
        return self._json_data


async def test_env_v2_settings_service_is_exposed(dt: DynatraceAsync):
    assert isinstance(dt.account.settings, SettingService)


async def test_env_v2_settings_list_effective_values(dt: DynatraceAsync):
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
        if (method, path) == ("GET", "/api/v2/settings/effectiveValues"):
            return MockResponse(
                {
                    "items": [
                        {
                            "author": "author-1",
                            "created": 1710000000000,
                            "createdBy": "user-1",
                            "externalId": "ext-1",
                            "modified": 1710000100000,
                            "modifiedBy": "user-2",
                            "origin": "ENVIRONMENT",
                            "schemaId": "builtin:test",
                            "schemaVersion": "1.0.0",
                            "searchSummary": "summary",
                            "summary": "effective",
                            "value": {"enabled": True},
                        }
                    ],
                    "totalCount": 1,
                }
            )

        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        effective_values = await dt.account.settings.list_effective_values(
            scope="environment"
        )

    assert isinstance(effective_values, PaginatedList)
    effective_values_list = await collect(effective_values)
    assert len(effective_values_list) == 1
    assert isinstance(effective_values_list[0], EffectiveSettingsValue)
    assert effective_values_list[0].schema_id == "builtin:test"
