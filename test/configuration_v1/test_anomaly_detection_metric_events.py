from dynatrace import DynatraceAsync
from dynatrace.configuration_v1.metric_events import (
    AggregationType,
    DisabledReason,
    MetricEventAutoAdaptiveBaselineMonitoringStrategy,
    MetricEventDimensionsFilterType,
    MetricEventMonitoringStrategyType,
    MetricEventShortRepresentation,
    MetricEventStaticThresholdMonitoringStrategy,
    Severity,
    Unit,
    WarningReason,
)
from dynatrace.pagination import PaginatedList
from test.async_utils import collect

STATIC_ID = "ruxit.python.rabbitmq:node_status:node_failed"
STATIC_NAME = "RabbitMQ Node failed"
BASELINE_ID = "d3baaaed-3441-4931-bf24-25c4e12e137f"
BASELINE_NAME = "Mint alert for static"


async def test_list(dt: DynatraceAsync):
    metric_events = await dt.anomaly_detection_metric_events.list()
    assert isinstance(metric_events, PaginatedList)

    list_metric_events = await collect(metric_events)
    assert len(list_metric_events) == 193

    first = list_metric_events[0]
    assert isinstance(first, MetricEventShortRepresentation)

    assert first.id == STATIC_ID
    assert first.name == STATIC_NAME


async def test_get_full_configuration(dt: DynatraceAsync):
    metric_events = await dt.anomaly_detection_metric_events.list()
    list_metric_events = await collect(metric_events)

    for metric_event in list_metric_events:
        if metric_event.id == STATIC_ID:
            # static
            full = await metric_event.get_full_metric_event()

            # type checks
            assert isinstance(full.name, str)
            assert isinstance(full.metric_id, str)
            assert isinstance(full.severity, Severity)
            assert isinstance(full.enabled, bool)
            assert isinstance(full.disabled_reason, DisabledReason)
            assert isinstance(full.aggregation_type, AggregationType)
            assert isinstance(full.warning_reason, WarningReason)
            assert isinstance(full.alerting_scope, list)
            assert isinstance(
                full.monitoring_strategy, MetricEventStaticThresholdMonitoringStrategy
            )
            assert isinstance(full.metric_dimensions, list)
            assert isinstance(full.primary_dimension_key, type(None))

            # value checks
            assert full.name == STATIC_NAME
            assert full.id == STATIC_ID
            assert full.aggregation_type == AggregationType.VALUE
            assert full.severity == Severity.AVAILABILITY
            assert full.enabled
            assert full.disabled_reason == DisabledReason.NONE
            assert (
                full.monitoring_strategy.type
                == MetricEventMonitoringStrategyType.STATIC_THRESHOLD
            )
            assert full.monitoring_strategy.unit == Unit.COUNT
            assert full.monitoring_strategy.violating_samples == 3
            assert (
                full.metric_dimensions[0].filter_type
                == MetricEventDimensionsFilterType.STRING
            )

        elif metric_event.id == BASELINE_ID:
            # static
            full = await metric_event.get_full_metric_event()

            # type checks
            assert isinstance(
                full.monitoring_strategy,
                MetricEventAutoAdaptiveBaselineMonitoringStrategy,
            )

            # value checks
            assert (
                full.monitoring_strategy.type
                == MetricEventMonitoringStrategyType.AUTO_ADAPTIVE_BASELINE
            )

            break

        else:
            continue
