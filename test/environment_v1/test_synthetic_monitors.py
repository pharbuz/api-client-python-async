from dynatrace import DynatraceAsync
from dynatrace.environment_v1.synthetic_monitors import (
    CreatedFrom,
    ManagementZone,
    MonitorCollectionElement,
    MonitorType,
)
from dynatrace.pagination import PaginatedList


async def test_list_string(dt: DynatraceAsync):
    monitors = await dt.synthetic_monitors.list(monitor_type="BROWSER")
    assert isinstance(monitors, PaginatedList)
    async for monitor in monitors:
        assert isinstance(monitor, MonitorCollectionElement)
        assert monitor.name == "angular easytravel bounce"
        assert monitor.entity_id == "SYNTHETIC_TEST-7639A3AED66940FA"
        assert monitor.monitor_type == "BROWSER"
        assert monitor.enabled
        break


async def test_list_enum(dt: DynatraceAsync):
    monitors = await dt.synthetic_monitors.list(monitor_type=MonitorType.BROWSER)
    assert isinstance(monitors, PaginatedList)
    async for monitor in monitors:
        assert isinstance(monitor, MonitorCollectionElement)
        assert monitor.name == "angular easytravel bounce"
        assert monitor.entity_id == "SYNTHETIC_TEST-7639A3AED66940FA"
        assert monitor.monitor_type == "BROWSER"
        assert monitor.enabled
        break


async def test_get_full_synthetic_config(dt: DynatraceAsync):
    config = await dt.synthetic_monitors.get_full_monitor_configuration(
        monitor_id="SYNTHETIC_TEST-7639A3AED66940FA"
    )
    assert config.name == "angular easytravel bounce"
    assert config.frequency_min == 5
    assert config.enabled
    assert config.type == MonitorType.BROWSER
    assert config.created_from == CreatedFrom.API
    assert isinstance(config.script, dict)
    assert (
        config.anomaly_detection.outage_handling.local_outage_policy.consecutive_runs
        == 1
    )
    assert not config.anomaly_detection.loading_time_thresholds.enabled
    for mz in config.management_zones:
        assert isinstance(mz, ManagementZone)
        break
