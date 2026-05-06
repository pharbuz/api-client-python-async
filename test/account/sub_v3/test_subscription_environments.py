import json
from unittest import mock

from dynatrace import DynatraceAsync
from dynatrace.account.sub_v3.environments import (
    EnvironmentCostResponse,
    EnvironmentUsageResponse,
    SubscriptionEnvironmentService,
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


async def test_subscription_environments_service_is_exposed(dt: DynatraceAsync):
    assert isinstance(dt.account.sub_v3, SubscriptionEnvironmentService)


async def test_subscription_environments_returns_expected_models(dt: DynatraceAsync):
    account_uuid = "account-123"
    subscription_uuid = "subscription-789"

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
        if (
            method,
            path,
        ) == (
            "GET",
            f"/sub/v3/accounts/{account_uuid}/subscriptions/{subscription_uuid}/environments/cost",
        ):
            return MockResponse(
                {
                    "data": [
                        {
                            "clusterId": "cluster-1",
                            "environmentId": "environment-1",
                            "cost": [
                                {
                                    "startTime": "2026-04-01",
                                    "endTime": "2026-04-02",
                                    "value": 3.14,
                                    "currencyCode": "USD",
                                    "capabilityKey": "metric",
                                    "capabilityName": "Metrics",
                                    "bookingDate": "2026-04-02",
                                }
                            ],
                        }
                    ],
                    "lastModifiedTime": "2026-04-02T00:00:00Z",
                    "nextPageKey": None,
                }
            )

        if (
            method,
            path,
        ) == (
            "GET",
            f"/sub/v3/accounts/{account_uuid}/subscriptions/{subscription_uuid}/environments/usage",
        ):
            return MockResponse(
                {
                    "data": [
                        {
                            "clusterId": "cluster-1",
                            "environmentId": "environment-1",
                            "usage": [
                                {
                                    "startTime": "2026-04-01",
                                    "endTime": "2026-04-02",
                                    "value": 1.0,
                                    "unitMeasure": "h",
                                    "capabilityKey": "metric",
                                    "capabilityName": "Metrics",
                                }
                            ],
                        }
                    ],
                    "lastModifiedTime": "2026-04-02T00:00:00Z",
                    "nextPageKey": None,
                }
            )

        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        usage_cost = await dt.account.sub_v3.cost(
            account_uuid,
            subscription_uuid,
            "2026-04-01",
            "2026-04-02",
        )
        usage = await dt.account.sub_v3.usage(
            account_uuid,
            subscription_uuid,
            "2026-04-01",
            "2026-04-02",
        )

    assert isinstance(usage_cost, EnvironmentCostResponse)
    assert usage_cost.data[0].environment_id == "environment-1"
    assert isinstance(usage, EnvironmentUsageResponse)
    assert usage.data[0].environment_id == "environment-1"
