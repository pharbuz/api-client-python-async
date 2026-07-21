import json
from unittest import mock

from dynatrace import DynatraceAsync
from dynatrace.account.sub_v2.subscriptions import (
    SubscriptionDetail,
    SubscriptionEnvironmentCostResponse,
    SubscriptionEnvironmentUsageResponse,
    SubscriptionForecast,
    SubscriptionService,
    SubscriptionSummary,
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


async def test_subscriptions_service_is_exposed(dt: DynatraceAsync):
    assert isinstance(dt.account.sub_v2, SubscriptionService)


async def test_subscriptions_service_returns_expected_models(dt: DynatraceAsync):
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
        if (method, path) == ("GET", f"/sub/v2/accounts/{account_uuid}/subscriptions"):
            return MockResponse(
                {
                    "data": [
                        {
                            "uuid": subscription_uuid,
                            "type": "STANDARD",
                            "name": "Sub 1",
                            "status": "ACTIVE",
                            "startTime": "2026-01-01",
                            "endTime": "2026-12-31",
                        }
                    ]
                }
            )

        if (method, path) == (
            "GET",
            f"/sub/v2/accounts/{account_uuid}/subscriptions/{subscription_uuid}",
        ):
            return MockResponse(
                {
                    "uuid": subscription_uuid,
                    "type": "STANDARD",
                    "name": "Sub 1",
                    "status": "ACTIVE",
                    "startTime": "2026-01-01",
                    "endTime": "2026-12-31",
                    "account": {"uuid": account_uuid},
                    "budget": {"total": 100.0, "used": 25.0, "currencyCode": "USD"},
                    "currentPeriod": {
                        "startTime": "2026-04-01",
                        "endTime": "2026-04-30",
                        "daysRemaining": 29,
                    },
                    "periods": [{"startTime": "2026-01-01", "endTime": "2026-03-31"}],
                    "capabilities": [{"key": "metric", "name": "Metrics"}],
                }
            )

        if (method, path) == (
            "GET",
            f"/sub/v2/accounts/{account_uuid}/subscriptions/forecast",
        ):
            return MockResponse(
                {
                    "forecastMedian": 42.0,
                    "forecastLower": 40.0,
                    "forecastUpper": 45.0,
                    "budget": 100.0,
                    "forecastBudgetPct": 42.0,
                    "forecastBudgetDate": "2026-05-01",
                    "forecastCreatedAt": "2026-04-02T00:00:00Z",
                }
            )

        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        subscriptions = await dt.account.sub_v2.list(account_uuid)
        subscription = await dt.account.sub_v2.get(account_uuid, subscription_uuid)
        forecast = await dt.account.sub_v2.forecast(account_uuid)

    assert isinstance(subscriptions, list)
    assert len(subscriptions) == 1
    assert isinstance(subscriptions[0], SubscriptionSummary)
    assert isinstance(subscription, SubscriptionDetail)
    assert subscription.uuid == subscription_uuid
    assert isinstance(forecast, SubscriptionForecast)
    assert forecast.budget == 100.0


async def test_subscription_environment_v2_returns_expected_models(
    dt: DynatraceAsync,
):
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
        expected_params = {
            "startTime": "2026-04-01",
            "endTime": "2026-04-02",
            "environmentIds": "environment-1,environment-2",
            "capabilityKeys": "metric,log",
        }

        if (method, path) == (
            "GET",
            f"/sub/v2/accounts/{account_uuid}/subscriptions/{subscription_uuid}/environments/usage",
        ):
            assert params == expected_params
            return MockResponse(
                {
                    "data": [
                        {
                            "environmentId": "environment-1",
                            "usage": [
                                {
                                    "capabilityKey": "metric",
                                    "capabilityName": "Metrics",
                                    "startTime": "2026-04-01",
                                    "endTime": "2026-04-02",
                                    "value": 1.5,
                                    "unitMeasure": "GiB",
                                }
                            ],
                        }
                    ],
                    "lastModifiedTime": "2026-04-02T00:00:00Z",
                }
            )

        if (method, path) == (
            "GET",
            f"/sub/v2/accounts/{account_uuid}/subscriptions/{subscription_uuid}/environments/cost",
        ):
            assert params == expected_params
            return MockResponse(
                {
                    "data": [
                        {
                            "environmentId": "environment-1",
                            "cost": [
                                {
                                    "capabilityKey": "metric",
                                    "capabilityName": "Metrics",
                                    "startTime": "2026-04-01",
                                    "endTime": "2026-04-02",
                                    "value": 3.14,
                                    "currencyCode": "USD",
                                }
                            ],
                        }
                    ],
                    "lastModifiedTime": "2026-04-02T00:00:00Z",
                }
            )

        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        usage = await dt.account.sub_v2.environment_usage(
            account_uuid,
            subscription_uuid,
            "2026-04-01",
            "2026-04-02",
            environment_ids=["environment-1", "environment-2"],
            capability_keys=["metric", "log"],
        )
        cost = await dt.account.sub_v2.environment_cost(
            account_uuid,
            subscription_uuid,
            "2026-04-01",
            "2026-04-02",
            environment_ids=["environment-1", "environment-2"],
            capability_keys=["metric", "log"],
        )

    assert isinstance(usage, SubscriptionEnvironmentUsageResponse)
    assert usage.data[0].environment_id == "environment-1"
    assert usage.data[0].usage[0].capability_key == "metric"
    assert usage.data[0].usage[0].value == 1.5
    assert usage.last_modified_time == "2026-04-02T00:00:00Z"
    assert isinstance(cost, SubscriptionEnvironmentCostResponse)
    assert cost.data[0].environment_id == "environment-1"
    assert cost.data[0].cost[0].currency_code == "USD"
    assert cost.data[0].cost[0].capability_name == "Metrics"
