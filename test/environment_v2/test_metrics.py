from dynatrace import DynatraceAsync
from dynatrace.environment_v2.metrics import (
    AggregationType,
    MetricDescriptor,
    MetricSeriesCollection,
    Transformation,
    ValueType,
)
from dynatrace.pagination import PaginatedList
from dynatrace.utils import int64_to_datetime
from test.async_utils import first


async def test_list(dt: DynatraceAsync):
    metrics = await dt.metrics.list()
    assert isinstance(metrics, PaginatedList)
    metric = await first(metrics)
    assert isinstance(metric, MetricDescriptor)
    assert metric.metric_id == "builtin:apps.other.apdex.osAndGeo"
    assert metric.display_name == "Apdex (by OS, geolocation) [mobile, custom]"
    assert metric.description == ""
    assert metric.unit == "NotApplicable"


async def test_list_fields(dt: DynatraceAsync):
    metrics = await dt.metrics.list(
        fields="+tags,+dduBillable,+created,+lastWritten,+aggregationTypes,+defaultAggregation,+dimensionDefinitions,+transformations,+entityType"
    )
    assert isinstance(metrics, PaginatedList)

    metric = await first(metrics)
    assert isinstance(metric, MetricDescriptor)
    assert metric.metric_id == "builtin:apps.other.apdex.osAndGeo"
    assert metric.display_name == "Apdex (by OS, geolocation) [mobile, custom]"
    assert metric.description == ""
    assert metric.unit == "NotApplicable"
    assert not metric.ddu_billable
    assert metric.created is None
    assert metric.last_written == int64_to_datetime(1620514220905)
    assert metric.entity_type == ["CUSTOM_APPLICATION", "MOBILE_APPLICATION"]
    assert metric.aggregation_types == [
        AggregationType.AUTO,
        AggregationType.AUTO.VALUE,
    ]
    assert Transformation.FOLD in metric.transformations
    assert metric.default_aggregation.type == "value"
    assert len(metric.dimension_definitions) == 3
    assert metric.dimension_definitions[0].key == "dt.entity.device_application"
    assert metric.dimension_definitions[0].name == "Application"
    assert metric.dimension_definitions[0].index == 0
    assert metric.dimension_definitions[0].type == "ENTITY"


async def test_list_params(dt: DynatraceAsync):

    written_since = int64_to_datetime(1621029621)

    metrics = await dt.metrics.list(
        metric_selector="builtin:host.*",
        written_since=written_since,
        metadata_selector='unit("Percent")',
        fields="+tags,+dduBillable,+created,+lastWritten,+aggregationTypes,+defaultAggregation,+dimensionDefinitions,+transformations,+entityType",
    )

    metric = await first(metrics)
    assert metric.metric_id == "builtin:host.cpu.idle"
    assert metric.display_name == "CPU idle"
    assert metric.description == ""
    assert metric.unit == "Percent"
    assert not metric.ddu_billable
    assert metric.last_written == int64_to_datetime(1621030025348)
    assert metric.entity_type == ["HOST"]
    assert metric.default_aggregation.type == "avg"
    assert metric.tags == []
    assert metric.dimension_definitions[0].key == "dt.entity.host"


async def test_get(dt: DynatraceAsync):

    metric = await dt.metrics.get("builtin:host.cpu.idle")

    assert metric.metric_id == "builtin:host.cpu.idle"
    assert metric.display_name == "CPU idle"
    assert metric.description == ""
    assert metric.unit == "Percent"
    assert not metric.ddu_billable
    assert metric.last_written == int64_to_datetime(1621030565348)
    assert metric.entity_type == ["HOST"]
    assert metric.default_aggregation.type == "avg"
    assert metric.tags == []
    assert metric.dimension_definitions[0].key == "dt.entity.host"
    assert metric.metric_value_type.type == ValueType.SCORE


async def test_query(dt: DynatraceAsync):
    time_from = int64_to_datetime(1621020000000)
    time_to = int64_to_datetime(1621025000000)

    results = await dt.metrics.query(
        "builtin:host.cpu.idle", time_from=time_from, time_to=time_to
    )
    assert isinstance(results, PaginatedList)

    print("Asserting first element")
    first_result = await first(results)

    print("Start")
    assert isinstance(first_result, MetricSeriesCollection)
    assert first_result.metric_id == "builtin:host.cpu.idle"
    assert len(first_result.data) == 1

    first_data = first_result.data[0]
    assert first_data.dimension_map == {"dt.entity.host": "HOST-82F576674F19AC16"}
    assert first_data.dimensions == ["HOST-82F576674F19AC16"]
    assert len(first_data.timestamps) == 3
    assert len(first_data.timestamps) == len(first_data.values)
    assert first_data.timestamps[0] == int64_to_datetime(3151435100000)


async def test_ingest(dt: DynatraceAsync):
    ingest = await dt.metrics.ingest(["a 1", "b 2"])
    assert isinstance(ingest, dict)
    assert ingest["linesOk"] == 1
    assert ingest["linesInvalid"] == 0
    assert ingest["error"] is None
