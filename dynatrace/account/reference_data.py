"""Reference data API wrappers."""

import builtins
from typing import Any

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient


class ReferenceDataService:
    """/ref/v1 Reference data API."""

    def __init__(self, http_client: HttpClient) -> None:
        self.__http_client = http_client

    async def list_time_zones(self) -> builtins.list["TimeZone"]:
        """Lists all available time zones."""
        resp = (await self.__http_client.make_request("/ref/v1/time-zones")).json()
        return [TimeZone(raw_element=time_zone) for time_zone in resp]

    async def list_regions(self) -> builtins.list["Region"]:
        """Lists all available regions."""
        resp = (await self.__http_client.make_request("/ref/v1/regions")).json()
        return [Region(raw_element=region) for region in resp]

    async def list_account_permissions(self) -> builtins.list["Permission"]:
        """Lists all available account permissions."""
        resp = (
            await self.__http_client.make_request("/ref/v1/account/permissions")
        ).json()
        return [Permission(raw_element=permission) for permission in resp]


class TimeZone(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.display_name: str | None = raw_element.get("displayName")
        self.name: str | None = raw_element.get("name")


class Region(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.name: str | None = raw_element.get("name")


class Permission(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.id: str | None = raw_element.get("id")
        self.description: str | None = raw_element.get("description")
