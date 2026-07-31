import json
from typing import Any
from unittest import mock

from dynatrace import DynatraceAsync
from dynatrace.http_client import HttpClient
from dynatrace.platform.davis.analyzers import AnalyzerService


class MockResponse:
    def __init__(self, json_data: Any = None) -> None:
        self._json_data = json_data
        self.headers: dict[str, str] = {}
        self.text = json.dumps(json_data) if json_data is not None else ""
        self.status_code = 200

    def json(self) -> Any:
        return self._json_data


async def test_davis_analyzers_service_is_exposed(dt: DynatraceAsync) -> None:
    assert isinstance(dt.platform.davis_analyzers, AnalyzerService)


async def test_davis_analyzers_execute_returns_result(dt: DynatraceAsync) -> None:
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
            "POST",
            "/platform/davis/analyzers/v1/analyzers/demo:execute",
        ):
            return MockResponse(
                {
                    "requestToken": "analyzer-token",
                    "ttlInSeconds": 30,
                    "result": {
                        "resultId": "result-1",
                        "resultStatus": "SUCCESS",
                        "executionStatus": "DONE",
                    },
                }
            )

        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        analyzer = await dt.platform.davis_analyzers.execute("demo", {"value": 1})

    assert analyzer.request_token == "analyzer-token"
    assert analyzer.result is not None
    assert analyzer.result.result_id == "result-1"
