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
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList
from dynatrace.utils import (
    datetime_to_int64,
    raw_optional_bool,
    raw_optional_int,
    raw_optional_object,
    raw_optional_str,
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


class AutoUpdate(Enum):
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"


class OsType(Enum):
    AIX = "AIX"
    LINUX = "LINUX"
    WINDOWS = "WINDOWS"
    SOLARIS = "SOLARIS"
    ZOS = "ZOS"


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


# todo - create class objects for ModuleInfo[] and PluginInfo[]
class HostAgentInfo(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
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
        self.available_versions: list[str] | None = raw_element.get("availableVersions")
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
        self.networkzone_id: str | None = raw_optional_str(
            raw_element, "currentNetworkZoneId"
        )


# todo - incomplete + firstSeenTimestamp is of type integer, how do we work with that here?
class HostInfo(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.entity_id: str | None = raw_optional_str(raw_element, "entityId")
        self.display_name: str | None = raw_optional_str(raw_element, "displayName")
        self.discovered_name: str | None = raw_optional_str(
            raw_element, "discoveredName"
        )
        self.consumed_host_units: str | float | None = raw_optional_str_or_float(
            raw_element, "consumedHostUnits"
        )
        self.os_version: str | None = raw_optional_str(raw_element, "osVersion")
        self.host_group: HostGroup | None = raw_optional_object(
            raw_element, "hostGroup", lambda value: HostGroup(raw_element=value)
        )
        self.tags: list[TagInfo] = [
            TagInfo(raw_element=t) for t in raw_element.get("tags", [])
        ]
        self.os_type: OsType | None = (
            OsType(raw_element.get("osType")) if raw_element.get("osType") else None
        )


class HostGroup(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.me_id: str | None = raw_optional_str(raw_element, "meId")
        self.name: str | None = raw_optional_str(raw_element, "name")


class TagInfo(DynatraceObject):
    # todo - convert context to Enum
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.context: str = raw_required_str(raw_element, "context")
        self.key: str = raw_required_str(raw_element, "key")
        self.value: str | None = raw_optional_str(raw_element, "value")
