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

from httpx import Response

from dynatrace.configuration_v1.tile import Tile
from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.environment_v2.monitored_entities import EntityShortRepresentation
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList


class DashboardService:
    def __init__(self, http_client: HttpClient):
        self.__http_client = http_client

    async def list(
        self, owner: str = None, tags: list[str] = None
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

    async def post(self, body: dict):
        return await self.__http_client.make_request(
            "/api/config/v1/dashboards", params=body, method="POST"
        )

    async def put(self, dashboard_id: str, body: dict):
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
    def _create_from_raw_data(self, raw_element):
        if raw_element is None:
            raw_element = {}
        self.timeframe: str = raw_element.get("timeframe")
        self.management_zone: EntityShortRepresentation | None = (
            EntityShortRepresentation(
                self._http_client, None, raw_element.get("managementZone")
            )
            if raw_element.get("managementZone")
            else None
        )


class DashboardMetadata(DynatraceObject):
    def _create_from_raw_data(self, raw_element):
        # TODO - Schema changed, add extra fields dynamicFilters
        self.name: str = raw_element.get("name")
        self.shared: bool = raw_element.get("shared")
        self.owner: str = raw_element.get("owner")
        self.dashboard_filter: DashboardFilter = DashboardFilter(
            self._http_client, None, raw_element.get("dashboardFilter")
        )
        self.tags: list[str] = raw_element.get("tags")
        self.preset: bool = raw_element.get("preset")


class Dashboard(DynatraceObject):
    def _create_from_raw_data(self, raw_element):
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
        self.raw_json: dict = raw_element


class DashboardStub(DynatraceObject):
    async def delete(self) -> Response:
        """
        Deletes this dashboard
        """
        return await self._http_client.make_request(
            f"/api/config/v1/dashboards/{self.id}", method="DELETE"
        )

    def _create_from_raw_data(self, raw_element):
        self.id: str = raw_element.get("id")
        self.name: str = raw_element.get("name")
        self.owner: str = raw_element.get("owner")

    async def get_full_dashboard(self) -> Dashboard:
        """
        Gets the full dashboard for this stub
        """
        response = (
            await self._http_client.make_request(f"/api/config/v1/dashboards/{self.id}")
        ).json()
        return Dashboard(self._http_client, None, response)
