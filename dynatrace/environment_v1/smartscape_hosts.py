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
from dynatrace.pagination import HeaderPaginatedList
from dynatrace.utils import (
    datetime_to_int64,
    raw_optional_int,
    raw_optional_object,
    raw_optional_str,
    raw_optional_str_or_float,
    raw_required_str,
)


class RelativeTime(Enum):
    MIN = "min"
    FIVE_MINS = "5mins"
    TEN_MINS = "10mins"
    FIFTEEN_MINS = "15mins"
    THIRTY_MINS = "30mins"
    HOUR = "hour"
    TWO_HOURS = "2hours"
    SIX_HOURS = "6hours"
    DAY = "day"
    THREE_DAYS = "3days"


class OSArchitecture(Enum):
    ARM = "ARM"
    IA_SIXTY_FOUR = "IA64"
    PARISC = "PARISC"
    PPC = "PPC"
    PPCLE = "PPCLE"
    SYSTEM_THIRTY_NINTEY = "S390"
    SPARC = "SPARC"
    X_EIGHTY_SIX = "X86"
    ZOS = "ZOS"


class MonitoringMode(Enum):
    FULL_STACK = "FULL_STACK"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    OFF = "OFF"
    NONE = None


class TagInfo(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.context: str = raw_required_str(raw_element, "context")
        self.key: str = raw_required_str(raw_element, "key")
        self.value: str | None = raw_optional_str(raw_element, "value")


class AgentVersion(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.major: int | None = raw_optional_int(raw_element, "major")
        self.minor: int | None = raw_optional_int(raw_element, "minor")
        self.revision: int | None = raw_optional_int(raw_element, "revision")
        self.timestamp: str | None = raw_optional_str(raw_element, "timestamp")
        self.source_revision: str | None = raw_optional_str(
            raw_element, "sourceRevision"
        )


class HostGroup(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.me_id: str | None = raw_optional_str(raw_element, "meId")
        self.name: str | None = raw_optional_str(raw_element, "name")


class Host(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.entity_id: str | None = raw_optional_str(raw_element, "entityId")
        self.display_name: str | None = raw_optional_str(raw_element, "displayName")
        self.customized_name: str | None = raw_optional_str(
            raw_element, "customizedName"
        )
        self.discovered_name: str | None = raw_optional_str(
            raw_element, "discoveredName"
        )
        self.first_seen_timestamp: int | None = raw_optional_int(
            raw_element, "firstSeenTimestamp"
        )
        self.last_seen_timestamp: int | None = raw_optional_int(
            raw_element, "lastSeenTimestamp"
        )
        self.tags: list[TagInfo] = [
            TagInfo(raw_element=tag) for tag in raw_element.get("tags", [])
        ]
        self.os_type: str | None = raw_optional_str(raw_element, "osType")
        self.consumed_host_units: str | float | None = raw_optional_str_or_float(
            raw_element, "consumedHostUnits"
        )
        self.agent_version: AgentVersion | None = raw_optional_object(
            raw_element, "agentVersion", lambda value: AgentVersion(raw_element=value)
        )
        self.monitoring_mode: MonitoringMode | None = (
            MonitoringMode(raw_element["monitoringMode"])
            if raw_element.get("monitoringMode")
            else None
        )
        self.network_zone_id: str | None = raw_optional_str(
            raw_element, "networkZoneId"
        )
        self.host_group: HostGroup | None = raw_optional_object(
            raw_element, "hostGroup", lambda value: HostGroup(raw_element=value)
        )
        self.os_architecture: OSArchitecture | None = (
            OSArchitecture(raw_element["osArchitecture"])
            if raw_element.get("osArchitecture")
            else None
        )
        self.cpu_cores: int | None = raw_optional_int(raw_element, "cpuCores")
        self.os_version: str | None = raw_optional_str(raw_element, "osVersion")


class SmartScapeHostsService:
    def __init__(self, http_client: HttpClient):
        self.__http_client = http_client

    async def list(
        self,
        relative_time: RelativeTime | str | None = RelativeTime.THREE_DAYS,
        start_timestamp: datetime | str | None = None,
        end_timestamp: datetime | str | None = None,
        page_size: int = 200,
        management_zone: int | None = None,
        host_group_name: str | None = None,
    ) -> HeaderPaginatedList[Host]:
        """
        List all monitored hosts

        :param management_zone: Filter hosts by a management zone ID
            Default value : None
        :param host_group_name: Filter hosts by a host group name
            Default value : None
        :param relative_time: Relative time ranger to check for (72 hours if not set)
            Default value : RelativeTime.THREE_DAYS
        :param start_timestamp: the start timestamp of the requested timeframe, in milliseconds (UTC)
        :param end_timestamp: the end timestamp of the requested timeframe, in milliseconds (UTC)
        """
        params = {
            "pageSize": page_size,
            "relativeTime": (
                RelativeTime(relative_time).value if not start_timestamp else None
            ),
            "startTimestamp": datetime_to_int64(start_timestamp),
            "endTimestamp": datetime_to_int64(end_timestamp),
            "managementZone": management_zone if management_zone else None,
            "hostGroupName": host_group_name if host_group_name else None,
        }
        return await HeaderPaginatedList(
            Host, self.__http_client, "/api/v1/entity/infrastructure/hosts", params
        ).initialize()
