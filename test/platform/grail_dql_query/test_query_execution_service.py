import json
from unittest import mock

from dynatrace import DynatraceAsync
from dynatrace.http_client import HttpClient
from dynatrace.platform.grail_dql_query.query_execution import (
    QueryExecutionService,
    QueryStartResponse,
)


class MockResponse:
    def __init__(self, json_data=None, text=None, raise_json: bool = False):
        self._json_data = json_data
        self.headers = {}
        self.text = (
            text
            if text is not None
            else json.dumps(json_data) if json_data is not None else ""
        )
        self.status_code = 200
        self._raise_json = raise_json

    def json(self):
        if self._raise_json:
            raise ValueError("No JSON payload")
        return self._json_data


async def test_query_execution_service_is_exposed(dt: DynatraceAsync):
    assert isinstance(dt.platform.grail_query_execution, QueryExecutionService)


async def test_query_execution_execute_and_cancel(dt: DynatraceAsync):
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
            return MockResponse(text="accepted", raise_json=True)

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
    assert canceled.text == "accepted"
