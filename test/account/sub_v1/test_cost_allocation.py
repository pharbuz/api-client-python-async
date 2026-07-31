import json
from typing import Any
from unittest import mock

from dynatrace import DynatraceAsync
from dynatrace.account.sub_v1.cost_allocation import (
    CostAllocationResponse,
    CostAllocationService,
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


async def test_cost_allocation_service_is_exposed(dt: DynatraceAsync) -> None:
    assert isinstance(dt.account.sub_v1_cost_allocation, CostAllocationService)


async def test_cost_allocation_get_returns_response(dt: DynatraceAsync) -> None:
    subscription_uuid = "subscription-789"

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
