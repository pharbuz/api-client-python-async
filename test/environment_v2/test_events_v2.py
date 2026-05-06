from datetime import UTC, datetime

from dynatrace import DynatraceAsync
from dynatrace.environment_v2.custom_tags import METag
from dynatrace.environment_v2.events import (
    Event,
    EventProperty,
    EventSeverity,
    EventStatus,
    EventType,
)
from dynatrace.environment_v2.monitored_entities import EntityStub
from dynatrace.environment_v2.schemas import ManagementZone
from dynatrace.pagination import PaginatedList
from dynatrace.utils import int64_to_datetime
from test.async_utils import collect

EVENT_ID = "4578933396576863909_1631255744265"
EVENT_TYPE = "APPLICATION_OVERLOAD_PREVENTION"


async def test_list(dt: DynatraceAsync):
    events = await dt.events_v2.list(
        page_size=100,
        time_from=datetime.fromtimestamp(1599913748, UTC),
        time_to="1631258989895",
    )

    # type checks
    assert isinstance(events, PaginatedList)
    event_list = await collect(events)
    assert all(isinstance(e, Event) for e in event_list)

    # value checks
    assert len(event_list) == 3


async def test_get(dt: DynatraceAsync):
    event = await dt.events_v2.get(EVENT_ID)

    # type checks
    assert isinstance(event, Event)
    assert isinstance(event.start_time, datetime)
    assert isinstance(event.end_time, datetime)
    assert isinstance(event.event_type, str)
    assert isinstance(event.title, str)
    assert isinstance(event.entity_id, EntityStub)
    assert isinstance(event.properties, list)
    assert all(isinstance(p, EventProperty) for p in event.properties)
    assert isinstance(event.status, EventStatus)
    assert isinstance(event.entity_tags, list)
    assert all(isinstance(tag, METag) for tag in event.entity_tags)
    assert isinstance(event.management_zones, list)
    assert all(isinstance(mz, ManagementZone) for mz in event.management_zones)
    assert isinstance(event.under_maintenance, bool)
    assert isinstance(event.suppress_alert, bool)
    assert isinstance(event.suppress_problem, bool)
    assert isinstance(event.frequent_event, bool)

    # value checks
    assert event.event_id == EVENT_ID
    assert event.start_time == int64_to_datetime(1631255744265)
    assert event.end_time == int64_to_datetime(1631255744265)
    assert event.event_type == "CUSTOM_DEPLOYMENT"
    assert event.title == "Deployment"
    assert event.properties[0].key == "dt.event.group_label"
    assert event.properties[0].value == "Deployment"
    assert event.status == EventStatus.CLOSED
    assert not event.under_maintenance
    assert not event.suppress_alert
    assert not event.suppress_problem
    assert not event.frequent_event


async def test_list_types(dt: DynatraceAsync):
    event_types = await dt.events_v2.list_types()

    # type checks
    assert isinstance(event_types, PaginatedList)
    event_type_list = await collect(event_types)
    assert all(isinstance(et, EventType) for et in event_type_list)

    # value checks
    assert len(event_type_list) == 5


async def test_get_type(dt: DynatraceAsync):
    type_details = await dt.events_v2.get_type(EVENT_TYPE)

    # type checks
    assert isinstance(type_details, EventType)
    assert isinstance(type_details.type, str)
    assert isinstance(type_details.display_name, str)
    assert isinstance(type_details.severity_level, EventSeverity)
    assert isinstance(type_details.description, str)

    # value checks
    assert type_details.type == EVENT_TYPE
    assert type_details.display_name == "Application overload prevention"
    assert type_details.severity_level == EventSeverity.INFO
    assert type_details.description == "Max user actions per minute exceeded"


async def test_ingest(dt: DynatraceAsync):
    ingest = await dt.events_v2.ingest(
        "CUSTOM_ALERT",
        "Dt API Test",
        properties={"test": "test"},
        entity_selector="type(HOST)",
    )
    assert isinstance(ingest, dict)
    assert ingest["eventIngestResults"][0]["status"] == "OK"
