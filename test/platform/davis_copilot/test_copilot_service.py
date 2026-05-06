import json
from unittest import mock

from dynatrace import DynatraceAsync
from dynatrace.http_client import HttpClient
from dynatrace.platform.davis_copilot.copilot_service import (
    CopilotService,
    SkillType,
    Status,
)


class MockResponse:
    def __init__(
        self,
        json_data=None,
        headers=None,
        text=None,
        raise_json: bool = False,
    ):
        self._json_data = json_data
        self.headers = headers or {}
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


async def test_copilot_service_is_exposed(dt: DynatraceAsync):
    assert isinstance(dt.platform.davis_copilot, CopilotService)


async def test_copilot_service_returns_expected_models(dt: DynatraceAsync):
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
        if (method, path) == ("GET", "/platform/davis/copilot/v1/skills"):
            return MockResponse(
                {"skills": ["conversation", "nl2dql", "dql2nl", "documentSearch"]}
            )

        if (method, path) == (
            "POST",
            "/platform/davis/copilot/v1/skills/nl2dql:generate",
        ):
            return MockResponse(
                {
                    "dql": "fetch logs",
                    "messageToken": "token-1",
                    "status": "SUCCESSFUL",
                    "metadata": {},
                }
            )

        raise AssertionError(f"Unexpected request: {method} {path}")

    with mock.patch.object(HttpClient, "make_request", new=fake_make_request):
        skills = await dt.platform.davis_copilot.list_skills()
        generated = await dt.platform.davis_copilot.generate_dql_query(
            {"query": "fetch logs"}
        )

    assert [skill for skill in skills.skills] == [
        SkillType.CONVERSATION,
        SkillType.NL2DQL,
        SkillType.DQL2NL,
        SkillType.DOCUMENT_SEARCH,
    ]
    assert generated.dql == "fetch logs"
    assert generated.status == Status.SUCCESSFUL
