import json
from unittest import mock

from dynatrace import DynatraceAsync
from dynatrace.account.env_v1.environments import (
    AccountEnvironmentsV1Service,
    AccountEnvironmentsWithZones,
    IpAllowlistConfig,
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


async def test_env_v1_environments_service_is_exposed(dt: DynatraceAsync):
    assert isinstance(dt.account.env_v1, AccountEnvironmentsV1Service)


async def test_env_v1_environments_service_returns_expected_models(dt: DynatraceAsync):
    account_uuid = "account-123"
    environment_uuid = "environment-456"

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
        if (method, path) == ("GET", f"/env/v1/accounts/{account_uuid}/environments"):
            return MockResponse(
                {
                    "tenantResources": [{"name": "tenant-1", "id": "tenant-id-1"}],
                    "managementZoneResources": [
                        {"parent": "root", "name": "mz-1", "id": "mz-id-1"}
                    ],
                }
            )

        if (
            method,
            path,
        ) == (
            "GET",
            f"/env/v1/accounts/{account_uuid}/environments/{environment_uuid}/ip-allowlist",
        ):
            return MockResponse(
                {
                    "enabled": True,
                    "allowWebhookOverride": False,
                    "allowlist": [{"name": "office", "ipRange": "10.0.0.0/24"}],
                }
            )

        if (
            method,
            path,
        ) == (
            "PUT",
            f"/env/v1/accounts/{account_uuid}/environments/{environment_uuid}/ip-allowlist",
        ):
            return MockResponse({"ok": True})

        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        environments = await dt.account.env_v1.list(account_uuid)
        allowlist = await dt.account.env_v1.get_ip_allowlist(
            account_uuid, environment_uuid
        )
        put_result = await dt.account.env_v1.set_ip_allowlist(
            account_uuid, environment_uuid, allowlist
        )

    assert isinstance(environments, AccountEnvironmentsWithZones)
    assert environments.tenant_resources[0].name == "tenant-1"
    assert environments.management_zone_resources[0].name == "mz-1"
    assert isinstance(allowlist, IpAllowlistConfig)
    assert allowlist.allowlist[0].ip_range == "10.0.0.0/24"
    assert put_result.status_code == 200
