import json
from typing import Any
from unittest import mock

import pytest

from dynatrace import DynatraceAsync
from dynatrace.account.limits import (
    AccountLimit,
    AccountLimitsPage,
    AccountLimitsService,
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


async def test_account_limits_service_is_exposed(dt: DynatraceAsync) -> None:
    assert isinstance(dt.account.limits, AccountLimitsService)


async def test_account_limits_list_returns_models(dt: DynatraceAsync) -> None:
    account_uuid = "account-123"

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
        if (method, path) == ("GET", f"/iam/v1/accounts/{account_uuid}/limits"):
            return MockResponse(
                {
                    "pageSize": 2,
                    "pageNumber": 1,
                    "total": 2,
                    "results": [
                        {
                            "currentValue": 12,
                            "limitType": "GROUPS_PER_ACCOUNT",
                            "limitValue": 100,
                        },
                        {
                            "currentValue": 4,
                            "limitType": "SERVICE_USERS_PER_ACCOUNT",
                            "limitValue": 50,
                        },
                    ],
                }
            )

        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        limits = await dt.account.limits.list(account_uuid)

    assert isinstance(limits, AccountLimitsPage)
    assert limits.page_size == 2
    assert limits.page_number == 1
    assert limits.total == 2
    assert len(limits.results) == 2
    assert isinstance(limits.results[0], AccountLimit)
    assert limits.results[0].current_value == 12
    assert limits.results[0].limit_type == "GROUPS_PER_ACCOUNT"
    assert limits.results[0].limit_value == 100


def test_account_limits_reject_invalid_field_types() -> None:
    with pytest.raises(TypeError):
        AccountLimitsPage(raw_element={"pageSize": "2"})

    with pytest.raises(TypeError):
        AccountLimit(raw_element={"limitType": 123})
