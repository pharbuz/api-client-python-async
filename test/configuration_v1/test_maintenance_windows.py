from typing import Any

import pytest

from dynatrace import DynatraceAsync
from dynatrace.configuration_v1.maintenance_windows import (
    MaintenanceWindow,
    MaintenanceWindowCreated,
    MaintenanceWindowStub,
    MonitoredEntityFilter,
    Recurrence,
    Schedule,
    Scope,
    TagCombination,
)
from dynatrace.environment_v2.custom_tags import METag, TagContext
from dynatrace.environment_v2.monitored_entities import EntityShortRepresentation
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList
from test.async_utils import MockResponse, collect

ID = "b6376a12-0b82-4069-9a41-0e55ef9a1f44"
NAME = "Example Window"


async def test_list(dt: DynatraceAsync) -> None:
    mw = await dt.maintenance_windows.list()
    assert isinstance(mw, PaginatedList)

    list_mw = await collect(mw)
    assert len(list_mw) == 3

    first = list_mw[0]
    assert isinstance(first, MaintenanceWindowStub)

    assert first.id == ID
    assert first.name == NAME


async def test_get(dt: DynatraceAsync) -> None:
    mw = await dt.maintenance_windows.get(mw_id=ID)

    # type checks
    assert isinstance(mw, MaintenanceWindow)
    assert isinstance(mw.id, str)
    assert isinstance(mw.name, str)
    assert isinstance(mw.description, str)
    assert isinstance(mw.type, str)
    assert isinstance(mw.suppression, str)
    assert isinstance(mw.suppress_synthetic_monitors_execution, bool)
    assert isinstance(mw.scope, Scope)
    assert isinstance(mw.schedule, Schedule)

    assert all(isinstance(rule, MonitoredEntityFilter) for rule in mw.scope.matches)
    for rule in mw.scope.matches:
        assert isinstance(rule.type, str)
        assert isinstance(rule.mz_id, str)
        for t in rule.tags:
            assert isinstance(t, METag)
        assert isinstance(rule.tag_combination, TagCombination)

    # value checks
    assert mw.id == ID
    assert mw.name == NAME
    assert mw.description == "An example Maintenance window"
    assert mw.type == "UNPLANNED"
    assert mw.suppression == "DETECT_PROBLEMS_AND_ALERT"
    assert mw.suppress_synthetic_monitors_execution
    assert mw.scope.entities[0] == "HOST-0000000000123456"
    assert mw.scope.matches[0].type == "HOST"
    assert mw.scope.matches[0].mz_id == "-5283929364044076484"
    assert mw.scope.matches[0].tags[0].context == TagContext.AWS
    assert mw.scope.matches[0].tags[0].key == "testkey"
    assert mw.scope.matches[0].tags[0].value == "testvalue"
    assert mw.scope.matches[0].tag_combination == TagCombination.AND
    assert mw.schedule.recurrence_type == "ONCE"
    assert mw.schedule.recurrence is None
    assert mw.schedule.start_time == "2018-08-02 00:00"
    assert mw.schedule.end_time == "2021-02-27 00:00"
    assert mw.schedule.zone_id == "Europe/Vienna"


async def test_post(dt: DynatraceAsync) -> None:
    response = await dt.maintenance_windows.post(
        MaintenanceWindow(
            raw_element={
                "id": ID,
                "name": NAME,
                "description": "test_desc",
                "type": "PLANNED",
                "suppression": None,
                "suppressSyntheticMonitorsExecution": False,
                "schedule": {
                    "end": "2031-02-27 00:00",
                    "start": "2028-08-02 00:00",
                    "zoneId": "Europe/Vienna",
                    "recurrence": {
                        "dayOfWeek": None,
                        "dayOfMonth": None,
                        "startTime": None,
                        "durationMinutes": None,
                    },
                    "recurrenceType": "ONCE",
                },
                "scope": {
                    "entities": ["HOST-0000000000123456"],
                    "matches": [
                        {
                            "type": "HOST",
                            "mzId": "-5283929364044076484",
                            "tags": [
                                {
                                    "context": "AWS",
                                    "key": "testkey",
                                    "value": "testvalue",
                                }
                            ],
                            "tagCombination": "AND",
                        }
                    ],
                },
            }
        )
    )

    # type checks
    assert isinstance(response, EntityShortRepresentation)
    # value checks
    assert response.id == ID
    assert response.name == NAME


def test_monitored_entity_filter_omits_empty_tag_combination() -> None:
    entity_filter = MonitoredEntityFilter(raw_element={"type": "HOST"})

    assert entity_filter.to_json() == {"type": "HOST", "mzId": None, "tags": []}


async def test_create_uses_scope_and_recurrence(
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
        return MockResponse({"id": ID, "name": NAME, "description": "test_desc"})

    monkeypatch.setattr(HttpClient, "make_request", fake_make_request)

    schedule = dt.maintenance_windows.create_schedule(
        recurrence_type="WEEKLY",
        start="2028-08-02 00:00",
        end="2031-02-27 00:00",
        zone_id="Europe/Vienna",
    )
    recurrence = Recurrence.create(
        start_time="16:28", duration=60, day_of_week="thursday"
    )
    scope = Scope(
        raw_element={
            "entities": ["HOST-0000000000123456"],
            "matches": [
                {
                    "type": "HOST",
                    "mzId": "-5283929364044076484",
                    "tags": [
                        {"context": "AWS", "key": "testkey", "value": "testvalue"}
                    ],
                    "tagCombination": "AND",
                }
            ],
        }
    )

    response = await dt.maintenance_windows.create(
        name=NAME,
        description="test_desc",
        window_type="PLANNED",
        suppression="DETECT_PROBLEMS_AND_ALERT",
        schedule=schedule,
        suppress_synthetic=False,
        scope=scope,
        recurrence=recurrence,
    )

    assert isinstance(response, MaintenanceWindowCreated)
    assert calls == [
        {
            "path": "/api/config/v1/maintenanceWindows",
            "params": {
                "id": None,
                "name": NAME,
                "description": "test_desc",
                "type": "PLANNED",
                "suppression": "DETECT_PROBLEMS_AND_ALERT",
                "suppressSyntheticMonitorsExecution": False,
                "schedule": {
                    "recurrenceType": "WEEKLY",
                    "recurrence": {
                        "startTime": "16:28",
                        "durationMinutes": 60,
                        "dayOfWeek": "THURSDAY",
                    },
                    "start": "2028-08-02 00:00",
                    "end": "2031-02-27 00:00",
                    "zoneId": "Europe/Vienna",
                },
                "scope": {
                    "entities": ["HOST-0000000000123456"],
                    "matches": [
                        {
                            "type": "HOST",
                            "mzId": "-5283929364044076484",
                            "tags": [
                                {
                                    "context": "AWS",
                                    "key": "testkey",
                                    "value": "testvalue",
                                }
                            ],
                            "tagCombination": "AND",
                        }
                    ],
                },
            },
            "method": "POST",
        }
    ]


async def test_put_and_validate_use_openapi_paths(
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
        calls.append({"path": path, "method": method})
        return MockResponse(None)

    monkeypatch.setattr(HttpClient, "make_request", fake_make_request)

    mw = MaintenanceWindow(
        raw_element={
            "id": ID,
            "name": NAME,
            "description": "test_desc",
            "type": "PLANNED",
            "suppression": "DETECT_PROBLEMS_AND_ALERT",
            "schedule": {
                "end": "2031-02-27 00:00",
                "start": "2028-08-02 00:00",
                "zoneId": "Europe/Vienna",
                "recurrenceType": "ONCE",
            },
        }
    )

    await dt.maintenance_windows.put(mw)
    await dt.maintenance_windows.validate(mw)

    assert calls == [
        {"path": f"/api/config/v1/maintenanceWindows/{ID}", "method": "PUT"},
        {
            "path": f"/api/config/v1/maintenanceWindows/{ID}/validator",
            "method": "POST",
        },
    ]
