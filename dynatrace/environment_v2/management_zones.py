from typing import Any

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient


class ManagementZoneServiceV2:
    ENDPOINT = "/api/v2/settings/managementZones"

    def __init__(self, http_client: HttpClient):
        self.__http_client = http_client

    async def get(self, object_id: str) -> "ManagementZoneDetails":
        """Reads management zone details.

        :param object_id: The ID of the required settings object.
        :return: a ManagementZoneDetails object
        """
        response = (
            await self.__http_client.make_request(f"{self.ENDPOINT}/{object_id}")
        ).json()
        return ManagementZoneDetails(raw_element=response)


class ManagementZoneDetails(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.id: str = raw_element["id"]
