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

from typing import Any

from httpx import Response

from dynatrace.configuration_v1.tile import Tile
from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.environment_v2.monitored_entities import EntityShortRepresentation
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList
from dynatrace.utils import raw_optional_bool, raw_optional_str, raw_optional_str_list


class DashboardService:
    def __init__(self, http_client: HttpClient):
        self.__http_client = http_client

    async def list(
        self, owner: str | None = None, tags: list[str] | None = None
    ) -> PaginatedList["DashboardStub"]:
        """
        Lists all dashboards of the environment
        :param owner: The owner of the dashboard.
        :param tags: A list of tags applied to the dashboard.
            The dashboard must match all the specified tags.
        """
        params = {"owner": owner, "tags": tags}
        return await PaginatedList(
            DashboardStub,
            self.__http_client,
            "/api/config/v1/dashboards",
            params,
            list_item="dashboards",
        ).initialize()

    async def get(self, dashboard_id: str) -> "Dashboard":
        """
        Gets the properties of the specified dashboard
        """
        response = (
            await self.__http_client.make_request(
                f"/api/config/v1/dashboards/{dashboard_id}"
            )
        ).json()
        return Dashboard(self.__http_client, None, response)

    async def post(self, body: dict[str, Any]) -> Response:
        return await self.__http_client.make_request(
            "/api/config/v1/dashboards", params=body, method="POST"
        )

    async def put(self, dashboard_id: str, body: dict[str, Any]) -> Response:
        return await self.__http_client.make_request(
            f"/api/config/v1/dashboards/{dashboard_id}", params=body, method="PUT"
        )

    async def delete(self, dashboard_id: str) -> Response:
        """
        Deletes the specified dashboard
        """
        return await self.__http_client.make_request(
            f"/api/config/v1/dashboards/{dashboard_id}", method="DELETE"
        )


class DashboardFilter(DynatraceObject):
    def _create_from_raw_data(self, raw_element: Any) -> None:
        if raw_element is None:
            raw_element = {}
        self.timeframe: str | None = raw_optional_str(raw_element, "timeframe")
        self.management_zone: EntityShortRepresentation | None = (
            EntityShortRepresentation(
                self._http_client, None, raw_element.get("managementZone")
            )
            if raw_element.get("managementZone")
            else None
        )


class DashboardGenericTagFilter(DynatraceObject):
    def _create_from_raw_data(self, raw_element: Any) -> None:
        if raw_element is None:
            raw_element = {}
        self.display_name: str | None = raw_optional_str(raw_element, "displayName")
        self.entity_types: list[str] = raw_optional_str_list(raw_element, "entityTypes")
        self.suggestions_from_entity_type: str | None = raw_optional_str(
            raw_element, "suggestionsFromEntityType"
        )
        self.tag_key: str | None = raw_optional_str(raw_element, "tagKey")


class DynamicFilters(DynatraceObject):
    def _create_from_raw_data(self, raw_element: Any) -> None:
        if raw_element is None:
            raw_element = {}
        self.filters: list[str] = raw_optional_str_list(raw_element, "filters")
        self.generic_tag_filters: list[DashboardGenericTagFilter] = [
            DashboardGenericTagFilter(self._http_client, None, raw_filter)
            for raw_filter in raw_element.get("genericTagFilters", [])
        ]


class DashboardMetadata(DynatraceObject):
    def _create_from_raw_data(self, raw_element: Any) -> None:
        if raw_element is None:
            raw_element = {}
        self.name: str | None = raw_optional_str(raw_element, "name")
        self.shared: bool | None = raw_optional_bool(raw_element, "shared")
        self.owner: str | None = raw_optional_str(raw_element, "owner")
        self.dashboard_filter: DashboardFilter = DashboardFilter(
            self._http_client, None, raw_element.get("dashboardFilter")
        )
        self.dynamic_filters: DynamicFilters | None = (
            DynamicFilters(self._http_client, None, raw_element.get("dynamicFilters"))
            if raw_element.get("dynamicFilters") is not None
            else None
        )
        self.has_consistent_colors: bool | None = raw_optional_bool(
            raw_element, "hasConsistentColors"
        )
        self.tags: list[str] = raw_optional_str_list(raw_element, "tags")
        self.preset: bool | None = raw_optional_bool(raw_element, "preset")
        self.tiles_name_size: str | None = raw_optional_str(
            raw_element, "tilesNameSize"
        )


class Dashboard(DynatraceObject):
    def _create_from_raw_data(self, raw_element: Any) -> None:
        if raw_element is None:
            raw_element = {}
        self.id: str = raw_element.get("id")
        self.dashboard_metadata: DashboardMetadata = DashboardMetadata(
            self._http_client, None, raw_element.get("dashboardMetadata")
        )
        self.tiles: list[Tile] = [
            Tile(self._http_client, None, raw_tile)
            for raw_tile in raw_element.get("tiles", [])
        ]
        self.raw_json: dict[str, Any] = raw_element


class DashboardStub(DynatraceObject):
    async def delete(self) -> Response:
        """
        Deletes this dashboard
        """
        return await self._make_request(
            f"/api/config/v1/dashboards/{self.id}", method="DELETE"
        )

    def _create_from_raw_data(self, raw_element: Any) -> None:
        self.id: str = raw_element.get("id")
        self.name: str = raw_element.get("name")
        self.owner: str = raw_element.get("owner")

    async def get_full_dashboard(self) -> Dashboard:
        """
        Gets the full dashboard for this stub
        """
        response = (
            await self._make_request(f"/api/config/v1/dashboards/{self.id}")
        ).json()
        return Dashboard(self._http_client, None, response)
