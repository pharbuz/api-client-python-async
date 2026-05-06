import json
from unittest import mock

from dynatrace import DynatraceAsync
from dynatrace.http_client import HttpClient
from dynatrace.platform.grail_dql_query.query_assistance import (
    DQLTerminalNode,
    QueryAssistanceService,
)


class MockResponse:
    def __init__(self, json_data=None):
        self._json_data = json_data
        self.headers = {}
        self.text = json.dumps(json_data) if json_data is not None else ""
        self.status_code = 200

    def json(self):
        return self._json_data


async def test_query_assistance_service_is_exposed(dt: DynatraceAsync):
    assert isinstance(dt.platform.grail_query_assistance, QueryAssistanceService)


async def test_query_assistance_parse_returns_terminal_node(dt: DynatraceAsync):
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
