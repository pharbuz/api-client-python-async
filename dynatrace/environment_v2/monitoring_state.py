"""Client for the Environment API v2 monitoring state endpoint."""

from typing import Any

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList


class MonitoringStateService:
    """Lists monitoring states of process group instances."""

    ENDPOINT = "/api/v2/monitoringstate"

    def __init__(self, http_client: HttpClient):
        self.__http_client = http_client

    async def list(
        self,
        page_size: int | None = None,
        entity_selector: str | None = None,
        from_: str | None = None,
        to: str | None = None,
    ) -> PaginatedList["MonitoredEntityState"]:
        """List monitoring states of process group instances.

        :param page_size: Number of entries per page. The maximum is 500.
        :param entity_selector: Entity selector for process group instances.
        :param from_: Start of the requested timeframe. Defaults to ``now-24h``.
        :param to: End of the requested timeframe. Defaults to now.
        """
        params = {
            "pageSize": page_size,
            "entitySelector": entity_selector,
            "from": from_,
            "to": to,
        }
        return await PaginatedList(
            MonitoredEntityState,
            self.__http_client,
            target_url=self.ENDPOINT,
            target_params=params,
            list_item="monitoringStates",
        ).initialize()


class MonitoredEntityState(DynatraceObject):
    """Monitoring state of a process group instance."""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.entity_id: str | None = raw_element.get("entityId")
        self.params: list[MonitoredEntityStateParam] = [
            MonitoredEntityStateParam(raw_element=param)
            for param in raw_element.get("params", [])
        ]
        self.severity: str | None = raw_element.get("severity")
        self.state: str | None = raw_element.get("state")


class MonitoredEntityStateParam(DynatraceObject):
    """Key-value parameter attached to a monitoring state."""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.key: str | None = raw_element.get("key")
        self.values: str | None = raw_element.get("values")
