from datetime import datetime, timezone

from dynatrace.environment_v1.oneagents import (
    AutoUpdate,
    AvailabilityState,
    ConfiguredMonitoringMode,
    DetailedAvailabilityState,
    HostAgentInfo,
    HostInfo,
    ModuleInfo,
    ModuleInstance,
    ModuleType,
    MonitoringType,
    OsType,
    PluginInfo,
    PluginInstance,
    PluginState,
    TagContext,
    TagInfo,
    UpdateStatus,
)
from dynatrace.environment_v2.monitored_entities import EntityShortRepresentation


def test_host_agent_info_parses_openapi_models() -> None:
    host_agent = HostAgentInfo(
        raw_element={
            "active": True,
            "autoUpdateSetting": "ENABLED",
            "availabilityState": "MONITORED",
            "availableVersions": ["1.2.3"],
            "configuredMonitoringEnabled": True,
            "configuredMonitoringMode": "FULL_STACK",
            "currentActiveGateId": 42,
            "currentActiveGateIds": ["42", "43"],
            "currentNetworkZoneId": "default",
            "detailedAvailabilityState": "MONITORED_AGENT_REGISTERED",
            "faultyVersion": False,
            "hostInfo": {
                "entityId": "HOST-123",
                "displayName": "host-one",
                "discoveredName": "host-one.local",
                "customizedName": "custom-host",
                "consumedHostUnits": "1.0",
                "firstSeenTimestamp": 1620000000000,
                "lastSeenTimestamp": 1620003600000,
                "ipAddresses": ["10.0.0.1"],
                "cpuCores": 8,
                "logicalCpuCores": 16,
                "bitness": "64bit",
                "cloudType": "EC2",
                "monitoringMode": "FULL_STACK",
                "networkZoneId": "default",
                "osType": "LINUX",
                "osVersion": "Ubuntu",
                "hostGroup": {"meId": "HOST_GROUP-1", "name": "group"},
                "managementZones": [{"id": "mz-1", "name": "Production"}],
                "tags": [{"context": "AWS", "key": "env", "value": "prod"}],
            },
            "modules": [
                {
                    "moduleType": "JAVA",
                    "instances": [
                        {
                            "active": True,
                            "faultyVersion": False,
                            "instanceName": "app",
                            "moduleVersion": "1.2.3",
                        }
                    ],
                }
            ],
            "monitoringType": "FULL_STACK",
            "plugins": [
                {
                    "pluginName": "custom.python.demo",
                    "instances": [{"pluginVersion": "2.0.0", "state": "OK"}],
                }
            ],
            "unlicensed": False,
            "updateStatus": "UP2DATE",
        }
    )

    assert host_agent.active is True
    assert host_agent.auto_update == AutoUpdate.ENABLED
    assert host_agent.availability_state == AvailabilityState.MONITORED
    assert host_agent.available_versions == ["1.2.3"]
    assert host_agent.config_monitoring_enabled is True
    assert host_agent.configured_monitoring_mode == ConfiguredMonitoringMode.FULL_STACK
    assert host_agent.activegate_id == 42
    assert host_agent.activegate_ids == ["42", "43"]
    assert host_agent.networkzone_id == "default"
    assert (
        host_agent.detailed_availability_state
        == DetailedAvailabilityState.MONITORED_AGENT_REGISTERED
    )
    assert host_agent.faulty_version is False
    assert host_agent.monitoring_type == MonitoringType.FULL_STACK
    assert host_agent.update_status == UpdateStatus.UP2DATE
    assert host_agent.unlicensed is False

    assert isinstance(host_agent.host_info, HostInfo)
    assert host_agent.host_info.entity_id == "HOST-123"
    assert host_agent.host_info.display_name == "host-one"
    assert host_agent.host_info.discovered_name == "host-one.local"
    assert host_agent.host_info.customized_name == "custom-host"
    assert host_agent.host_info.consumed_host_units == "1.0"
    assert host_agent.host_info.first_seen_timestamp == datetime.fromtimestamp(
        1620000000000 / 1000, timezone.utc
    )
    assert host_agent.host_info.last_seen_timestamp == datetime.fromtimestamp(
        1620003600000 / 1000, timezone.utc
    )
    assert host_agent.host_info.ip_addresses == ["10.0.0.1"]
    assert host_agent.host_info.cpu_cores == 8
    assert host_agent.host_info.logical_cpu_cores == 16
    assert host_agent.host_info.bitness == "64bit"
    assert host_agent.host_info.cloud_type == "EC2"
    assert host_agent.host_info.monitoring_mode == "FULL_STACK"
    assert host_agent.host_info.network_zone_id == "default"
    assert host_agent.host_info.os_type == OsType.LINUX
    assert host_agent.host_info.os_version == "Ubuntu"
    assert host_agent.host_info.host_group is not None
    assert host_agent.host_info.host_group.me_id == "HOST_GROUP-1"
    assert host_agent.host_info.host_group.name == "group"
    assert len(host_agent.host_info.management_zones) == 1
    assert isinstance(
        host_agent.host_info.management_zones[0], EntityShortRepresentation
    )
    assert host_agent.host_info.management_zones[0].id == "mz-1"
    assert isinstance(host_agent.host_info.tags[0], TagInfo)
    assert host_agent.host_info.tags[0].context == TagContext.AWS
    assert host_agent.host_info.tags[0].key == "env"
    assert host_agent.host_info.tags[0].value == "prod"

    assert len(host_agent.modules) == 1
    assert isinstance(host_agent.modules[0], ModuleInfo)
    assert host_agent.modules[0].module_type == ModuleType.JAVA
    assert isinstance(host_agent.modules[0].instances[0], ModuleInstance)
    assert host_agent.modules[0].instances[0].active is True
    assert host_agent.modules[0].instances[0].faulty_version is False
    assert host_agent.modules[0].instances[0].instance_name == "app"
    assert host_agent.modules[0].instances[0].module_version == "1.2.3"

    assert len(host_agent.plugins) == 1
    assert isinstance(host_agent.plugins[0], PluginInfo)
    assert host_agent.plugins[0].plugin_name == "custom.python.demo"
    assert isinstance(host_agent.plugins[0].instances[0], PluginInstance)
    assert host_agent.plugins[0].instances[0].plugin_version == "2.0.0"
    assert host_agent.plugins[0].instances[0].state == PluginState.OK
