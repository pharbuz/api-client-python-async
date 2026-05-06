import json
from unittest import mock

from dynatrace import DynatraceAsync
from dynatrace.http_client import HttpClient
from dynatrace.platform.davis.analyzers import AnalyzerService


class MockResponse:
    def __init__(self, json_data=None):
        self._json_data = json_data
        self.headers = {}
        self.text = json.dumps(json_data) if json_data is not None else ""
        self.status_code = 200

    def json(self):
        return self._json_data


async def test_davis_analyzers_service_is_exposed(dt: DynatraceAsync):
    assert isinstance(dt.platform.davis_analyzers, AnalyzerService)


async def test_davis_analyzers_execute_returns_result(dt: DynatraceAsync):
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
