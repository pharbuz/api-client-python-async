from typing import Any

import pytest

from dynatrace import DynatraceAsync
from dynatrace.environment_v2.monitoring_state import (
    MonitoredEntityState,
    MonitoredEntityStateParam,
)
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList
from test.async_utils import MockResponse


async def test_list_monitoring_states(
    dt: DynatraceAsync, monkeypatch: pytest.MonkeyPatch
) -> None:
    requests: list[tuple[str, dict[str, Any] | None]] = []

    async def make_request(
        self: Any,
        path: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        method: str = "GET",
        data: Any = None,
        query_params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> MockResponse:
        requests.append((path, params))
        if len(requests) == 1:
            return MockResponse(
                {
                    "monitoringStates": [
                        {
                            "entityId": "PROCESS_GROUP_INSTANCE-123",
                            "params": [{"key": "pids", "values": "111,222"}],
                            "severity": "warning",
                            "state": "restart_required",
                        }
                    ],
                    "nextPageKey": "next-page",
                    "pageSize": 1,
                    "totalCount": 2,
                }
            )
        return MockResponse(
            {
                "monitoringStates": [
                    {
                        "entityId": "PROCESS_GROUP_INSTANCE-456",
                        "params": [],
                        "severity": "ok",
                        "state": "ok",
                    }
                ],
                "pageSize": 1,
                "totalCount": 2,
            }
        )

    monkeypatch.setattr(HttpClient, "make_request", make_request)

    states = await dt.monitoring_state.list(
        page_size=1,
        entity_selector='type("PROCESS_GROUP_INSTANCE")',
        from_="now-2h",
        to="now",
    )

    assert isinstance(states, PaginatedList)
    result = await states.to_list()
    assert len(result) == 2
    assert all(isinstance(state, MonitoredEntityState) for state in result)
    assert result[0].entity_id == "PROCESS_GROUP_INSTANCE-123"
    assert result[0].severity == "warning"
    assert result[0].state == "restart_required"
    assert len(result[0].params) == 1
    assert isinstance(result[0].params[0], MonitoredEntityStateParam)
    assert result[0].params[0].key == "pids"
    assert result[0].params[0].values == "111,222"
    assert requests == [
        (
            "/api/v2/monitoringstate",
            {
                "pageSize": 1,
                "entitySelector": 'type("PROCESS_GROUP_INSTANCE")',
                "from": "now-2h",
                "to": "now",
            },
        ),
        ("/api/v2/monitoringstate", {"nextPageKey": "next-page"}),
    ]
