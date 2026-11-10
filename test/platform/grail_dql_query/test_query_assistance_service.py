import json
from typing import Any
from unittest import mock

from dynatrace import DynatraceAsync
from dynatrace.http_client import HttpClient
from dynatrace.platform.grail_dql_query.query_assistance import (
    DQLTerminalNode,
    QueryAssistanceService,
)


class MockResponse:
    def __init__(self, json_data: Any = None) -> None:
        self._json_data = json_data
        self.headers: dict[str, str] = {}
        self.text = json.dumps(json_data) if json_data is not None else ""
        self.status_code = 200

    def json(self) -> Any:
        return self._json_data


async def test_query_assistance_service_is_exposed(dt: DynatraceAsync) -> None:
    assert isinstance(dt.platform.grail_query_assistance, QueryAssistanceService)


async def test_query_assistance_parse_returns_terminal_node(dt: DynatraceAsync) -> None:
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
        if (method, path) == ("POST", "/platform/storage/query/v1/query:parse"):
            return MockResponse(
                {
                    "nodeType": "TERMINAL",
                    "isOptional": False,
                    "canonicalString": "fetch logs",
                    "type": "QUERY",
                    "tokenPosition": {"start": {"column": 1, "index": 0, "line": 1}},
                }
            )

        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        parsed = await dt.platform.grail_query_assistance.parse("fetch logs")

    assert isinstance(parsed, DQLTerminalNode)
    assert parsed.canonical_string == "fetch logs"
