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

from enum import Enum
from typing import Any

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList
from dynatrace.utils import (
    raw_optional_bool,
    raw_optional_int,
    raw_optional_object,
    raw_optional_str,
    raw_required_bool,
    raw_required_int,
    raw_required_str,
)


class MonitorType(Enum):
    BROWSER = "BROWSER"
    HTTP = "HTTP"


class LoadingTimeThresholdType(Enum):
    ACTION = "ACTION"
    TOTAL = "TOTAL"


class TagSource(Enum):
    AUTO = "AUTO"
    RULE_BASED = "RULE_BASED"
    USER = "USER"


class CreatedFrom(Enum):
    API = "API"
    GUI = "GUI"


class TagContext(Enum):
    AWS = "AWS"
    AWS_GENERIC = "AWS_GENERIC"
    AZURE = "AZURE"
    CLOUD_FOUNDRY = "CLOUD_FOUNDRY"
    CONTEXTLESS = "CONTEXTLESS"
    ENVIRONMENT = "ENVIRONMENT"
    GOOGLE_CLOUD = "GOOGLE_CLOUD"
    KUBERNETES = "KUBERNETES"


class MonitorCollectionElement(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.name: str = raw_required_str(raw_element, "name")
        self.entity_id: str = raw_required_str(raw_element, "entityId")
        self.monitor_type: str = raw_required_str(raw_element, "type")
        self.enabled: bool = raw_required_bool(raw_element, "enabled")


class LocalOutagePolicy(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.affected_locations: int = raw_required_int(
            raw_element, "affectedLocations"
        )
        self.consecutive_runs: int = raw_required_int(raw_element, "consecutiveRuns")


class OutageHandlingPolicy(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.global_outage: bool = raw_required_bool(raw_element, "globalOutage")
        self.local_outage: bool = raw_required_bool(raw_element, "localOutage")
        self.local_outage_policy: LocalOutagePolicy = LocalOutagePolicy(
            raw_element=raw_element["localOutagePolicy"]
        )
        self.retry_on_error: bool | None = raw_optional_bool(
            raw_element, "retryOnError"
        )


class LoadingTimeThreshold(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.type: LoadingTimeThresholdType = LoadingTimeThresholdType(
            raw_element["type"]
        )
        self.value_ms: int = raw_required_int(raw_element, "valueMs")
        self.request_index: int | None = raw_optional_int(raw_element, "requestIndex")
        self.event_index: int | None = raw_optional_int(raw_element, "eventIndex")


class LoadingTimeThresholdsPolicyDto(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.enabled: bool = raw_required_bool(raw_element, "enabled")
        self.thresholds: list[LoadingTimeThreshold] = [
            LoadingTimeThreshold(raw_element=threshold)
            for threshold in raw_element["thresholds"]
        ]


class AnomalyDetection(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.outage_handling: OutageHandlingPolicy | None = raw_optional_object(
            raw_element,
            "outageHandling",
            lambda value: OutageHandlingPolicy(raw_element=value),
        )
        self.loading_time_thresholds: LoadingTimeThresholdsPolicyDto | None = (
            raw_optional_object(
                raw_element,
                "loadingTimeThresholds",
                lambda value: LoadingTimeThresholdsPolicyDto(raw_element=value),
            )
        )


class TagWithSourceInfo(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.source: TagSource | None = (
            TagSource(raw_element["source"]) if raw_element.get("source") else None
        )
        self.context: TagContext = TagContext(raw_element["context"])
        self.key: str = raw_required_str(raw_element, "key")
        self.value: str | None = raw_optional_str(raw_element, "value")


class ManagementZone(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.id: str = raw_required_str(raw_element, "id")
        self.name: str = raw_required_str(raw_element, "name")


class SyntheticMonitor(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.entity_id: str = raw_required_str(raw_element, "entityId")
        self.name: str = raw_required_str(raw_element, "name")
        self.frequency_min: int = raw_required_int(raw_element, "frequencyMin")
        self.enabled: bool = raw_required_bool(raw_element, "enabled")
        self.type: MonitorType = MonitorType(raw_element["type"])
        self.created_from: CreatedFrom = CreatedFrom(raw_element["createdFrom"])
        self.script: dict[str, Any] = raw_element["script"]
        self.locations: list[str] = raw_element["locations"]
        self.anomaly_detection: AnomalyDetection | None = raw_optional_object(
            raw_element,
            "anomalyDetection",
            lambda value: AnomalyDetection(raw_element=value),
        )
        self.tags: list[TagWithSourceInfo] = [
            TagWithSourceInfo(raw_element=tag) for tag in raw_element["tags"]
        ]
        self.management_zones: list[ManagementZone] = [
            ManagementZone(raw_element=zone) for zone in raw_element["managementZones"]
        ]
        self.automatically_assigned_apps: list[str] = raw_element[
            "automaticallyAssignedApps"
        ]
        self.manually_assigned_apps: list[str] = raw_element["manuallyAssignedApps"]


class SyntheticMonitorsService:
    def __init__(self, http_client: HttpClient):
        self.__http_client = http_client

    async def list(
        self, monitor_type: MonitorType | str | None = None
    ) -> PaginatedList[MonitorCollectionElement]:
        """
        Lists all synthetic monitors in the environment.
        """
        params = {"type": MonitorType(monitor_type).value if monitor_type else None}
        return await PaginatedList(
            MonitorCollectionElement,
            self.__http_client,
            "/api/v1/synthetic/monitors",
            target_params=params,
            list_item="monitors",
        ).initialize()

    async def get_full_monitor_configuration(self, monitor_id: str) -> SyntheticMonitor:
        """
        Get full monitor configuration for the specified monitor id (aka entity id).
        """
        return SyntheticMonitor(
            self.__http_client,
            raw_element=(
                await self.__http_client.make_request(
                    f"/api/v1/synthetic/monitors/{monitor_id}"
                )
            ).json(),
        )
