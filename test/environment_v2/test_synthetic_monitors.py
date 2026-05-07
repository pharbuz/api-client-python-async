from dynatrace import DynatraceAsync
from dynatrace.environment_v2.synthetic_monitors import (
    MonitorEntityId,
    SyntheticBrowserMonitor,
    SyntheticMonitorSummary,
    SyntheticMultiProtocolMonitor,
)

MULTI_MONITOR_ID = "MULTIPROTOCOL_MONITOR-63653CB579F573D1"
BROWSER_MONITOR_ID = "SYNTHETIC_TEST-3724112C5023ADB4"


async def test_list(dt: DynatraceAsync):
    monitors = await dt.synthetic_monitors_v2.list()

    assert isinstance(monitors, list)
    assert len(monitors) == 2
    assert all(isinstance(m, SyntheticMonitorSummary) for m in monitors)

    assert monitors[0].entity_id == MULTI_MONITOR_ID
    assert monitors[0].name == "My network availability monitor"
    assert monitors[0].type == "MULTI_PROTOCOL"
    assert monitors[0].enabled is True

    assert monitors[1].entity_id == BROWSER_MONITOR_ID
    assert monitors[1].name == "My browser monitor"
    assert monitors[1].type == "BROWSER"
    assert monitors[1].enabled is False


async def test_get_multi_protocol(dt: DynatraceAsync):
    monitor = await dt.synthetic_monitors_v2.get(monitor_id=MULTI_MONITOR_ID)

    assert isinstance(monitor, SyntheticMultiProtocolMonitor)
    assert monitor.entity_id == MULTI_MONITOR_ID
    assert monitor.name == "My network availability monitor"
    assert monitor.type == "MULTI_PROTOCOL"
    assert monitor.enabled is True
    assert monitor.frequency_min == 60
    assert isinstance(monitor.locations, list)
    assert isinstance(monitor.steps, list)
    assert isinstance(monitor.performance_thresholds, dict)
    assert isinstance(monitor.synthetic_monitor_outage_handling_settings, dict)
    assert isinstance(monitor.tags, list)
    assert isinstance(monitor.primary_grail_tags, list)


async def test_get_browser(dt: DynatraceAsync):
    monitor = await dt.synthetic_monitors_v2.get(monitor_id=BROWSER_MONITOR_ID)

    assert isinstance(monitor, SyntheticBrowserMonitor)
    assert monitor.entity_id == BROWSER_MONITOR_ID
    assert monitor.name == "My browser monitor"
    assert monitor.type == "BROWSER"
    assert monitor.enabled is True
    assert monitor.frequency_min == 15
    assert isinstance(monitor.locations, list)
    assert isinstance(monitor.steps, list)
    assert isinstance(monitor.configuration, dict)
    assert isinstance(monitor.key_performance_metrics, dict)
    assert isinstance(monitor.performance_thresholds, dict)
    assert isinstance(monitor.synthetic_monitor_outage_handling_settings, dict)
    assert isinstance(monitor.tags, list)
    assert isinstance(monitor.primary_grail_tags, list)
    assert isinstance(monitor.automatically_assigned_entities, list)
    assert isinstance(monitor.manually_assigned_entities, list)
    assert isinstance(monitor.cookies, list)


async def test_create(dt: DynatraceAsync):
    body = {
        "name": "Test Monitor",
        "type": "MULTI_PROTOCOL",
        "locations": ["SYNTHETIC_LOCATION-123"],
        "steps": [
            {
                "name": "Step 1",
                "requestType": "ICMP",
                "targetList": ["127.0.0.1"],
            }
        ],
    }
    result = await dt.synthetic_monitors_v2.create(body=body)

    assert isinstance(result, MonitorEntityId)
    assert result.entity_id == "MULTIPROTOCOL_MONITOR-NEW1234567890ABCDEF"


async def test_update(dt: DynatraceAsync):
    body = {
        "name": "Updated Monitor",
        "enabled": False,
        "type": "MULTI_PROTOCOL",
        "locations": ["SYNTHETIC_LOCATION-123"],
        "steps": [
            {
                "name": "Step 1",
                "requestType": "ICMP",
                "targetList": ["127.0.0.1"],
            }
        ],
    }
    response = await dt.synthetic_monitors_v2.update(MULTI_MONITOR_ID, body=body)
    assert response.status_code == 200


async def test_delete(dt: DynatraceAsync):
    response = await dt.synthetic_monitors_v2.delete(monitor_id=MULTI_MONITOR_ID)
    assert response.status_code == 200
