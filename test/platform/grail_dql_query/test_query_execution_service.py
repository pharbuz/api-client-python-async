import json
from typing import Any
from unittest import mock

from httpx import Response

from dynatrace import DynatraceAsync
from dynatrace.http_client import HttpClient
from dynatrace.platform.grail_dql_query.query_execution import (
    QueryExecutionService,
    QueryStartResponse,
)


class MockResponse:
    def __init__(
        self, json_data: Any = None, text: str | None = None, raise_json: bool = False
    ) -> None:
        self._json_data = json_data
        self.headers: dict[str, str] = {}
        self.text = (
            text
            if text is not None
            else json.dumps(json_data) if json_data is not None else ""
        )
        self.status_code = 200
        self._raise_json = raise_json

    def json(self) -> Any:
        if self._raise_json:
            raise ValueError("No JSON payload")
        return self._json_data


async def test_query_execution_service_is_exposed(dt: DynatraceAsync) -> None:
    assert isinstance(dt.platform.grail_query_execution, QueryExecutionService)


async def test_query_execution_execute_and_cancel(dt: DynatraceAsync) -> None:
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
    ) -> MockResponse | Response:
        if (method, path) == ("POST", "/platform/storage/query/v1/query:execute"):
            return MockResponse(
                {
                    "progress": 100,
                    "requestToken": "request-token-1",
                    "state": "SUCCESSFUL",
                    "ttlSeconds": 60,
                    "result": {
                        "metadata": {"grail": {"queryId": "query-1"}},
                        "records": [{"message": "hello"}],
                        "types": [],
                    },
                }
            )

        if (method, path) == ("POST", "/platform/storage/query/v1/query:cancel"):
            return Response(200, text="accepted")

        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        started = await dt.platform.grail_query_execution.execute("fetch logs")
        canceled = await dt.platform.grail_query_execution.cancel("request-token-1")

    assert isinstance(started, QueryStartResponse)
    assert started.request_token == "request-token-1"
    assert started.result is not None
    assert started.result.metadata is not None
    assert started.result.metadata.grail is not None
    assert started.result.metadata.grail.query_id == "query-1"
    assert isinstance(canceled, Response)
    assert canceled.text == "accepted"
