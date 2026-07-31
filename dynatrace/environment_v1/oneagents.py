"""
Copyright 2021 Dynatrace LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.environment_v2.monitored_entities import EntityShortRepresentation
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList
from dynatrace.utils import (
    datetime_to_int64,
    int64_to_datetime,
    raw_optional_bool,
    raw_optional_enum_or_str,
    raw_optional_int,
    raw_optional_object,
    raw_optional_str,
    raw_optional_str_list,
    raw_optional_str_or_float,
    raw_required_str,
)


class ConfiguredMonitoringMode(Enum):
    CLOUD_INFRASTRUCTURE = "CLOUD_INFRASTRUCTURE"
    DISCOVERY = "DISCOVERY"
    FULL_STACK = "FULL_STACK"


class UpdateStatus(Enum):
    INCOMPATIBLE = "INCOMPATIBLE"
    OUTDATED = "OUTDATED"
    SCHEDULED = "SCHEDULED"
    SUPPRESSED = "SUPPRESSED"
    UNKNOWN = "UNKNOWN"
    UP2DATE = "UP2DATE"
    UPDATE_IN_PROGRESS = "UPDATE_IN_PROGRESS"
    UPDATE_PENDING = "UPDATE_PENDING"
    UPDATE_PROBLEM = "UPDATE_PROBLEM"
    NONE = None


class MonitoringType(Enum):
    CLOUD_INFRASTRUCTURE = "CLOUD_INFRASTRUCTURE"
    DISCOVERY = "DISCOVERY"
    FULL_STACK = "FULL_STACK"
    STANDALONE = "STANDALONE"


class AvailabilityState(Enum):
    MONITORED = "MONITORED"
    UNMONITORED = "UNMONITORED"
    CRASHED = "CRASHED"
    LOST = "LOST"
    PRE_MONITORED = "PRE_MONITORED"
    SHUTDOWN = "SHUTDOWN"
    UNEXPECTED_SHUTDOWN = "UNEXPECTED_SHUTDOWN"
    UNKNOWN = "UNKNOWN"


class DetailedAvailabilityState(Enum):
    CRASHED_FAILURE = "CRASHED_FAILURE"
    CRASHED_UNKNOWN = "CRASHED_UNKNOWN"
    LOST_AGENT_UPGRADE_FAILED = "LOST_AGENT_UPGRADE_FAILED"
    LOST_CONNECTION = "LOST_CONNECTION"
    LOST_UNKNOWN = "LOST_UNKNOWN"
    MONITORED = "MONITORED"
    MONITORED_AGENT_ENABLED = "MONITORED_AGENT_ENABLED"
    MONITORED_AGENT_REGISTERED = "MONITORED_AGENT_REGISTERED"
    MONITORED_AGENT_UPGRADE_STARTED = "MONITORED_AGENT_UPGRADE_STARTED"
    MONITORED_AGENT_VERSION_ACCEPTED = "MONITORED_AGENT_VERSION_ACCEPTED"
    MONITORED_ENABLED = "MONITORED_ENABLED"
    PRE_MONITORED = "PRE_MONITORED"
    SHUTDOWN_AGENT_LOST = "SHUTDOWN_AGENT_LOST"
    SHUTDOWN_GRACEFUL = "SHUTDOWN_GRACEFUL"
    SHUTDOWN_K8S_NODE_SHUTDOWN = "SHUTDOWN_K8S_NODE_SHUTDOWN"
    SHUTDOWN_SPOT_INSTANCE = "SHUTDOWN_SPOT_INSTANCE"
    SHUTDOWN_STOPPED = "SHUTDOWN_STOPPED"
    SHUTDOWN_UNKNOWN = "SHUTDOWN_UNKNOWN"
    SHUTDOWN_UNKNOWN_UNEXPECTED = "SHUTDOWN_UNKNOWN_UNEXPECTED"
    UNKNOWN = "UNKNOWN"
    UNMONITORED_AGENT_DISABLED = "UNMONITORED_AGENT_DISABLED"
    UNMONITORED_AGENT_LOST = "UNMONITORED_AGENT_LOST"
    UNMONITORED_AGENT_MIGRATED = "UNMONITORED_AGENT_MIGRATED"
    UNMONITORED_AGENT_RESTART_TRIGGERED = "UNMONITORED_AGENT_RESTART_TRIGGERED"
    UNMONITORED_AGENT_STOPPED = "UNMONITORED_AGENT_STOPPED"
    UNMONITORED_AGENT_UNINSTALLED = "UNMONITORED_AGENT_UNINSTALLED"
    UNMONITORED_AGENT_UNREGISTERED = "UNMONITORED_AGENT_UNREGISTERED"
    UNMONITORED_AGENT_UPGRADE_FAILED = "UNMONITORED_AGENT_UPGRADE_FAILED"
    UNMONITORED_AGENT_VERSION_REJECTED = "UNMONITORED_AGENT_VERSION_REJECTED"
    UNMONITORED_DISABLED = "UNMONITORED_DISABLED"
    UNMONITORED_ID_CHANGED = "UNMONITORED_ID_CHANGED"
    UNMONITORED_TERMINATED = "UNMONITORED_TERMINATED"
    UNMONITORED_UNKNOWN = "UNMONITORED_UNKNOWN"


class AutoUpdate(Enum):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class OsType(Enum):
    AIX = "AIX"
    DARWIN = "DARWIN"
    HPUX = "HPUX"
    LINUX = "LINUX"
    WINDOWS = "WINDOWS"
    SOLARIS = "SOLARIS"
    ZOS = "ZOS"


class TagContext(Enum):
    AWS = "AWS"
    AWS_GENERIC = "AWS_GENERIC"
    AZURE = "AZURE"
    CLOUD_FOUNDRY = "CLOUD_FOUNDRY"
    CONTEXTLESS = "CONTEXTLESS"
    ENVIRONMENT = "ENVIRONMENT"
    GOOGLE_CLOUD = "GOOGLE_CLOUD"
    KUBERNETES = "KUBERNETES"


class ModuleType(Enum):
    APACHE = "APACHE"
    DOT_NET = "DOT_NET"
    DUMPPROC = "DUMPPROC"
    GO = "GO"
    IBM_INTEGRATION_BUS = "IBM_INTEGRATION_BUS"
    IIS = "IIS"
    JAVA = "JAVA"
    LOG_ANALYTICS = "LOG_ANALYTICS"
    NETTRACER = "NETTRACER"
    NETWORK = "NETWORK"
    NGINX = "NGINX"
    NODE_JS = "NODE_JS"
    OPENTRACINGNATIVE = "OPENTRACINGNATIVE"
    PHP = "PHP"
    PROCESS = "PROCESS"
    PYTHON = "PYTHON"
    RUBY = "RUBY"
    SDK = "SDK"
    UPDATER = "UPDATER"
    VARNISH = "VARNISH"
    Z_OS = "Z_OS"


class PluginState(Enum):
    DISABLED = "DISABLED"
    ERROR_AUTH = "ERROR_AUTH"
    ERROR_COMMUNICATION_FAILURE = "ERROR_COMMUNICATION_FAILURE"
    ERROR_CONFIG = "ERROR_CONFIG"
    ERROR_TIMEOUT = "ERROR_TIMEOUT"
    ERROR_UNKNOWN = "ERROR_UNKNOWN"
    INCOMPATIBLE = "INCOMPATIBLE"
    LIMIT_REACHED = "LIMIT_REACHED"
    NOTHING_TO_REPORT = "NOTHING_TO_REPORT"
    OK = "OK"
    STATE_TYPE_UNKNOWN = "STATE_TYPE_UNKNOWN"
    UNINITIALIZED = "UNINITIALIZED"
    UNSUPPORTED = "UNSUPPORTED"
    WAITING_FOR_STATE = "WAITING_FOR_STATE"


class OneAgentOnAHostService:
    def __init__(self, http_client: HttpClient):
        self.__http_client = http_client

    async def list(
        self,
        include_details: bool | None = None,
        start_timestamp: datetime | int | None = None,
        end_timestamp: datetime | int | None = None,
        relative_time: str | None = None,
        tag: list[str] | None = None,
        entity: list[str] | None = None,
        mz_id: str | None = None,
        management_zone: str | None = None,
        network_zone_id: str | None = None,
        host_group_id: str | None = None,
        host_group_name: str | None = None,
        os_type: OsType | str | None = None,
        availability_state: AvailabilityState | str | None = None,
        monitoring_type: MonitoringType | str | None = None,
        auto_update: AutoUpdate | str | None = None,
        update_status: UpdateStatus | str | None = None,
    ) -> PaginatedList["HostAgentInfo"]:
        """
        Lists OneAgents on a Host. Older API - timestamps are of type integer and therefore require conversion
        """
        params = {
            "includeDetails": include_details,
            "startTimestamp": datetime_to_int64(start_timestamp),
            "endTimestamp": datetime_to_int64(end_timestamp),
            "relativeTime": relative_time,
            "tag": tag,
            "entity": entity,
            "managementZoneId": mz_id,
            "managementZone": management_zone,
            "networkZoneId": network_zone_id,
            "hostGroupId": host_group_id,
            "hostGroupName": host_group_name,
            "osType": OsType(os_type).value if os_type else None,
            "availabilityState": (
                AvailabilityState(availability_state).value
                if availability_state
                else None
            ),
            "monitoringType": (
                MonitoringType(monitoring_type).value if monitoring_type else None
            ),
            "autoUpdateSetting": AutoUpdate(auto_update).value if auto_update else None,
            "updateStatus": (
                UpdateStatus(update_status).value if update_status else None
            ),
        }
        return await PaginatedList(
            HostAgentInfo,
            self.__http_client,
            "/api/v1/oneagents",
            params,
            list_item="hosts",
        ).initialize()


class ModuleInstance(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.active: bool | None = raw_optional_bool(raw_element, "active")
        self.faulty_version: bool | None = raw_optional_bool(
            raw_element, "faultyVersion"
        )
        self.instance_name: str | None = raw_optional_str(raw_element, "instanceName")
        self.module_version: str | None = raw_optional_str(raw_element, "moduleVersion")


class ModuleInfo(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.instances: list[ModuleInstance] = [
            ModuleInstance(raw_element=instance)
            for instance in raw_element.get("instances", [])
        ]
        self.module_type: ModuleType | None = (
            ModuleType(raw_element["moduleType"])
            if raw_element.get("moduleType")
            else None
        )


class PluginInstance(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.plugin_version: str | None = raw_optional_str(raw_element, "pluginVersion")
        self.state: PluginState | str | None = raw_optional_enum_or_str(
            PluginState, raw_element.get("state")
        )


class PluginInfo(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.instances: list[PluginInstance] = [
            PluginInstance(raw_element=instance)
            for instance in raw_element.get("instances", [])
        ]
        self.plugin_name: str | None = raw_optional_str(raw_element, "pluginName")


class HostAgentInfo(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.host_info: HostInfo | None = raw_optional_object(
            raw_element, "hostInfo", lambda value: HostInfo(raw_element=value)
        )
        self.faulty_version: bool | None = raw_optional_bool(
            raw_element, "faultyVersion"
        )
        self.active: bool | None = raw_optional_bool(raw_element, "active")
        self.configured_monitoring_mode: ConfiguredMonitoringMode | None = (
            ConfiguredMonitoringMode(raw_element["configuredMonitoringMode"])
            if raw_element.get("configuredMonitoringMode")
            else None
        )
        self.monitoring_type: MonitoringType | None = (
            MonitoringType(raw_element["monitoringType"])
            if raw_element.get("monitoringType")
            else None
        )
        self.auto_update: AutoUpdate | None = (
            AutoUpdate(raw_element["autoUpdateSetting"])
            if raw_element.get("autoUpdateSetting")
            else None
        )
        self.update_status: UpdateStatus | None = (
            UpdateStatus(raw_element["updateStatus"])
            if raw_element.get("updateStatus")
            else None
        )
        self.available_versions: list[str] = raw_optional_str_list(
            raw_element, "availableVersions"
        )
        self.config_monitoring_enabled: bool | None = raw_optional_bool(
            raw_element, "configuredMonitoringEnabled"
        )
        self.availability_state: AvailabilityState | None = (
            AvailabilityState(raw_element["availabilityState"])
            if raw_element.get("availabilityState")
            else None
        )
        self.activegate_id: int | None = raw_optional_int(
            raw_element, "currentActiveGateId"
        )
        self.activegate_ids: list[str] = raw_optional_str_list(
            raw_element, "currentActiveGateIds"
        )
        self.networkzone_id: str | None = raw_optional_str(
            raw_element, "currentNetworkZoneId"
        )
        self.detailed_availability_state: DetailedAvailabilityState | None = (
            DetailedAvailabilityState(raw_element["detailedAvailabilityState"])
            if raw_element.get("detailedAvailabilityState")
            else None
        )
        self.modules: list[ModuleInfo] = [
            ModuleInfo(raw_element=module) for module in raw_element.get("modules", [])
        ]
        self.plugins: list[PluginInfo] = [
            PluginInfo(raw_element=plugin) for plugin in raw_element.get("plugins", [])
        ]
        self.unlicensed: bool | None = raw_optional_bool(raw_element, "unlicensed")


class HostInfo(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.entity_id: str | None = raw_optional_str(raw_element, "entityId")
        self.display_name: str | None = raw_optional_str(raw_element, "displayName")
        self.discovered_name: str | None = raw_optional_str(
            raw_element, "discoveredName"
        )
        self.consumed_host_units: str | float | None = raw_optional_str_or_float(
            raw_element, "consumedHostUnits"
        )
        self.customized_name: str | None = raw_optional_str(
            raw_element, "customizedName"
        )
        self.first_seen_timestamp: datetime | None = int64_to_datetime(
            raw_element.get("firstSeenTimestamp")
        )
        self.last_seen_timestamp: datetime | None = int64_to_datetime(
            raw_element.get("lastSeenTimestamp")
        )
        self.ip_addresses: list[str] = raw_optional_str_list(raw_element, "ipAddresses")
        self.cpu_cores: int | None = raw_optional_int(raw_element, "cpuCores")
        self.logical_cpu_cores: int | None = raw_optional_int(
            raw_element, "logicalCpuCores"
        )
        self.bitness: str | None = raw_optional_str(raw_element, "bitness")
        self.cloud_type: str | None = raw_optional_str(raw_element, "cloudType")
        self.monitoring_mode: str | None = raw_optional_str(
            raw_element, "monitoringMode"
        )
        self.network_zone_id: str | None = raw_optional_str(
            raw_element, "networkZoneId"
        )
        self.os_version: str | None = raw_optional_str(raw_element, "osVersion")
        self.host_group: HostGroup | None = raw_optional_object(
            raw_element, "hostGroup", lambda value: HostGroup(raw_element=value)
        )
        self.management_zones: list[EntityShortRepresentation] = [
            EntityShortRepresentation(raw_element=management_zone)
            for management_zone in raw_element.get("managementZones", [])
        ]
        self.tags: list[TagInfo] = [
            TagInfo(raw_element=t) for t in raw_element.get("tags", [])
        ]
        self.os_type: OsType | None = (
            OsType(raw_element.get("osType")) if raw_element.get("osType") else None
        )
        self.raw_json: dict[str, Any] = raw_element


class HostGroup(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.me_id: str | None = raw_optional_str(raw_element, "meId")
        self.name: str | None = raw_optional_str(raw_element, "name")


class TagInfo(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.context: TagContext = TagContext(raw_required_str(raw_element, "context"))
        self.key: str = raw_required_str(raw_element, "key")
        self.value: str | None = raw_optional_str(raw_element, "value")
