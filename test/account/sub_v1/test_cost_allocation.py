import json
from unittest import mock

from dynatrace import DynatraceAsync
from dynatrace.account.sub_v1.cost_allocation import (
    CostAllocationResponse,
    CostAllocationService,
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


async def test_cost_allocation_service_is_exposed(dt: DynatraceAsync):
    assert isinstance(dt.account.sub_v1_cost_allocation, CostAllocationService)


async def test_cost_allocation_get_returns_response(dt: DynatraceAsync):
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
        if (method, path) == (
            "GET",
            f"/v1/subscriptions/{subscription_uuid}/cost-allocation",
        ):
            return MockResponse(
                {
                    "environmentId": "environment-1",
                    "field": "PRODUCT",
                    "records": [{"value": 10}],
                    "nextPageKey": None,
                }
            )

        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        cost_allocation = await dt.account.sub_v1_cost_allocation.get(
            subscription_uuid, field="PRODUCT"
        )

    assert isinstance(cost_allocation, CostAllocationResponse)
    assert cost_allocation.field == "PRODUCT"
