from datetime import datetime
from typing import Any

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient
from dynatrace.utils import raw_optional_datetime


class SyntheticMonitorService:
    ENDPOINT = "/api/v2/synthetic/monitors"

    def __init__(self, http_client: HttpClient):
        self.__http_client = http_client

    async def list(
        self, monitor_selector: str | None = None
    ) -> list["SyntheticMonitorSummary"]:
        """Gets all synthetic monitors.

        :param monitor_selector: Defines the scope of the query.
            Only monitors matching the specified criteria are included into response.
        :return: a list of SyntheticMonitorSummary objects
        """
        params = {"monitorSelector": monitor_selector}
        response = (
            await self.__http_client.make_request(path=self.ENDPOINT, params=params)
        ).json()
        return [
            SyntheticMonitorSummary(raw_element=m) for m in response.get("monitors", [])
        ]

    async def get(
        self, monitor_id: str
    ) -> "SyntheticMultiProtocolMonitor | SyntheticBrowserMonitor":
        """Gets a synthetic monitor definition for the given monitor ID.

        :param monitor_id: The identifier of the monitor.
        :return: a SyntheticMultiProtocolMonitor or SyntheticBrowserMonitor
        """
        response = (
            await self.__http_client.make_request(f"{self.ENDPOINT}/{monitor_id}")
        ).json()
        monitor_type = response.get("type", "")
        if monitor_type == "BROWSER":
            return SyntheticBrowserMonitor(raw_element=response)
        return SyntheticMultiProtocolMonitor(raw_element=response)

    async def create(self, body: dict[str, Any]) -> "MonitorEntityId":
        """Creates a synthetic monitor definition.

        :param body: The JSON body of the request. Contains the parameters of the monitor.
            For BROWSER type use SyntheticBrowserMonitorRequest schema.
            For MULTI_PROTOCOL type use SyntheticMultiProtocolMonitorRequest schema.
        :return: MonitorEntityId with the created monitor's entity ID
        """
        response = (
            await self.__http_client.make_request(
                path=self.ENDPOINT, params=body, method="POST"
            )
        ).json()
        return MonitorEntityId(raw_element=response)

    async def update(self, monitor_id: str, body: dict[str, Any]):
        """Updates a synthetic monitor definition for the given monitor ID.

        :param monitor_id: The identifier of the monitor.
        :param body: The JSON body of the request. Contains the parameters of the monitor.
        :return: HTTP response
        """
        return await self.__http_client.make_request(
            path=f"{self.ENDPOINT}/{monitor_id}", params=body, method="PUT"
        )

    async def delete(self, monitor_id: str):
        """Deletes a synthetic monitor definition for the given monitor ID.

        :param monitor_id: The identifier of the monitor.
        :return: HTTP response
        """
        return await self.__http_client.make_request(
            path=f"{self.ENDPOINT}/{monitor_id}", method="DELETE"
        )


class SyntheticMonitorSummary(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.enabled: bool = raw_element.get("enabled", True)
        self.entity_id: str = raw_element["entityId"]
        self.name: str = raw_element["name"]
        self.type: str = raw_element["type"]


class MonitorEntityId(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.entity_id: str = raw_element["entityId"]


class SyntheticBrowserMonitor(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.automatically_assigned_entities: list[str] = raw_element.get(
            "automaticallyAssignedEntities", []
        )
        self.configuration: dict = raw_element.get("configuration", {})
        self.description: str | None = raw_element.get("description")
        self.enabled: bool = raw_element.get("enabled", True)
        self.entity_id: str = raw_element["entityId"]
        self.frequency_min: int = raw_element["frequencyMin"]
        self.key_performance_metrics: dict = raw_element.get(
            "keyPerformanceMetrics", {}
        )
        self.locations: list[str] = raw_element.get("locations", [])
        self.manually_assigned_entities: list[str] = raw_element.get(
            "manuallyAssignedEntities", []
        )
        self.modification_timestamp: datetime | None = raw_optional_datetime(
            raw_element, "modificationTimestamp"
        )
        self.name: str = raw_element.get("name", "")
        self.performance_thresholds: dict = raw_element.get("performanceThresholds", {})
        self.primary_grail_tags: list[dict] = raw_element.get("primaryGrailTags", [])
        self.steps: list[dict] = raw_element.get("steps", [])
        self.synthetic_monitor_outage_handling_settings: dict = raw_element.get(
            "syntheticMonitorOutageHandlingSettings", {}
        )
        self.tags: list[dict] = raw_element.get("tags", [])
        self.type: str = raw_element["type"]
        self.cookies: list[dict] = raw_element.get("cookies", [])


class SyntheticMultiProtocolMonitor(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.description: str | None = raw_element.get("description")
        self.enabled: bool = raw_element.get("enabled", True)
        self.entity_id: str = raw_element["entityId"]
        self.frequency_min: int = raw_element["frequencyMin"]
        self.locations: list[str] = raw_element.get("locations", [])
        self.modification_timestamp: datetime | None = raw_optional_datetime(
            raw_element, "modificationTimestamp"
        )
        self.name: str = raw_element.get("name", "")
        self.performance_thresholds: dict = raw_element.get("performanceThresholds", {})
        self.primary_grail_tags: list[dict] = raw_element.get("primaryGrailTags", [])
        self.steps: list[dict] = raw_element.get("steps", [])
        self.synthetic_monitor_outage_handling_settings: dict = raw_element.get(
            "syntheticMonitorOutageHandlingSettings", {}
        )
        self.tags: list[dict] = raw_element.get("tags", [])
        self.type: str = raw_element["type"]
