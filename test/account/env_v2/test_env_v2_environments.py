import json
from unittest import mock

from dynatrace import DynatraceAsync
from dynatrace.account.env_v2.environments import (
    AccountClustersResponse,
    AccountEnvironmentsV2Response,
    AccountEnvironmentsV2Service,
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


async def test_env_v2_environments_service_is_exposed(dt: DynatraceAsync):
    assert isinstance(dt.account.env_v2, AccountEnvironmentsV2Service)


async def test_env_v2_environments_service_returns_expected_models(dt: DynatraceAsync):
    account_uuid = "account-123"

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
        if (method, path) == ("GET", f"/env/v2/accounts/{account_uuid}/environments"):
            return MockResponse(
                {
                    "data": [
                        {
                            "id": "env-1",
                            "name": "Environment 1",
                            "active": True,
                            "url": "https://example",
                        }
                    ]
                }
            )

        if (method, path) == ("GET", f"/env/v2/accounts/{account_uuid}/clusters"):
            return MockResponse({"data": [{"clusterId": "cluster-1"}]})

        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        env_v2_environments = await dt.account.env_v2.list_environments(account_uuid)
        env_v2_clusters = await dt.account.env_v2.list_clusters(account_uuid)

    assert isinstance(env_v2_environments, AccountEnvironmentsV2Response)
    assert env_v2_environments.data[0].id == "env-1"
    assert isinstance(env_v2_clusters, AccountClustersResponse)
    assert env_v2_clusters.data[0].cluster_id == "cluster-1"
