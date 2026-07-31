from datetime import datetime, timezone
from typing import Any

import pytest

from dynatrace import DynatraceAsync
from dynatrace.environment_v2.audit_logs import AuditLogEntry, EventType, UserType
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList
from test.async_utils import MockResponse, collect


async def test_list(dt: DynatraceAsync) -> None:
    audit_logs = await dt.audit_logs.list()
    assert isinstance(audit_logs, PaginatedList)

    audit_logs_list = await collect(audit_logs)
    assert len(audit_logs_list) == 6

    first = audit_logs_list[0]
    assert isinstance(first, AuditLogEntry)
    assert first.log_id == "162100314800090003"
    assert first.event_type == EventType("DELETE")
    assert first.category == "CONFIG"
    assert (
        first.entity_id
        == "builtin:alerting.profile (tenant): d89472d3-f9f4-420d-9398-768bb3351e85: test"
    )
    assert first.environment_id == "eaa50379"
    assert first.user == "Dynatrace support user #649982176"
    assert first.user_type == UserType("USER_NAME")
    assert first.user_origin == "webui (xxx.xxx.xxx.xxx)"
    assert first.timestamp == datetime.fromtimestamp(1621003148800 / 1000, timezone.utc)
    assert first.success


async def test_get(dt: DynatraceAsync) -> None:
    audit_log = await dt.audit_logs.get("162100314800090003")
    assert isinstance(audit_log, AuditLogEntry)
    assert audit_log.log_id == "162100314800090003"
    assert audit_log.event_type == EventType("DELETE")
    assert audit_log.category == "CONFIG"
    assert (
        audit_log.entity_id
        == "builtin:alerting.profile (tenant): d89472d3-f9f4-420d-9398-768bb3351e85: test"
    )
    assert audit_log.environment_id == "eaa50379"
    assert audit_log.user == "Dynatrace support user #649982176"
    assert audit_log.user_type == UserType("USER_NAME")
    assert audit_log.user_origin == "webui (xxx.xxx.xxx.xxx)"
    assert audit_log.timestamp == datetime.fromtimestamp(
        1621003148800 / 1000, timezone.utc
    )
    assert audit_log.success


def test_audit_log_entry_parses_settings_fields_and_any_patch() -> None:
    audit_log = AuditLogEntry(
        raw_element={
            "category": "CONFIG",
            "dt.settings.key": "builtin:example",
            "dt.settings.object_id": "object-id",
            "dt.settings.object_summary": "summary",
            "dt.settings.schema_id": "schema-id",
            "dt.settings.scope_id": "environment",
            "dt.settings.scope_name": "Environment",
            "environmentId": "env-id",
            "eventType": "REORDER",
            "logId": "197425568800060000",
            "patch": {"op": "replace", "path": "/value"},
            "success": True,
            "timestamp": 1974255688445,
            "user": "test.user@company.com",
            "userType": "USER_NAME",
        }
    )

    assert audit_log.event_type == EventType.REORDER
    assert audit_log.patch == {"op": "replace", "path": "/value"}
    assert audit_log.settings_key == "builtin:example"
    assert audit_log.settings_object_id == "object-id"
    assert audit_log.settings_object_summary == "summary"
    assert audit_log.settings_schema_id == "schema-id"
    assert audit_log.settings_scope_id == "environment"
    assert audit_log.settings_scope_name == "Environment"


async def test_list_accepts_openapi_page_size_parameter(
    dt: DynatraceAsync, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[dict[str, Any]] = []

    async def fake_make_request(
        self: HttpClient,
        path: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        method: str = "GET",
        data: Any = None,
        query_params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> MockResponse:
        calls.append({"path": path, "params": params, "method": method})
        return MockResponse({"auditLogs": [], "totalCount": 0})

    monkeypatch.setattr(HttpClient, "make_request", fake_make_request)

    audit_logs = await dt.audit_logs.list(page_size=5000, sort="timestamp")
    await collect(audit_logs)

    assert calls == [
        {
            "path": "/api/v2/auditlogs",
            "params": {
                "filter": None,
                "from": None,
                "to": None,
                "sort": "timestamp",
                "pageSize": 5000,
            },
            "method": "GET",
        }
    ]
