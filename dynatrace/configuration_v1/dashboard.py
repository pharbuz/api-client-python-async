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
from dynatrace.environment_v2.schemas import ConfigurationMetadata
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList
from dynatrace.utils import (
    raw_optional_bool,
    raw_optional_int,
    raw_optional_object,
    raw_optional_str,
    raw_optional_str_dict,
    raw_optional_str_list_or_none,
    raw_required_object,
    raw_required_object_list,
    raw_required_str,
    raw_required_str_list,
)


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

    async def get_share_settings(self, dashboard_id: str) -> "DashboardSharing":
        response = (
            await self.__http_client.make_request(
                f"/api/config/v1/dashboards/{dashboard_id}/shareSettings"
            )
        ).json()
        return DashboardSharing(self.__http_client, None, response)

    async def put_share_settings(
        self, dashboard_id: str, sharing: "DashboardSharing"
    ) -> Response:
        return await self.__http_client.make_request(
            f"/api/config/v1/dashboards/{dashboard_id}/shareSettings",
            params=sharing.to_json(),
            method="PUT",
        )

    async def validate_share_settings(
        self, dashboard_id: str, sharing: "DashboardSharing"
    ) -> Response:
        return await self.__http_client.make_request(
            f"/api/config/v1/dashboards/{dashboard_id}/shareSettings/validator",
            params=sharing.to_json(),
            method="POST",
        )

    async def delete(self, dashboard_id: str) -> Response:
        """
        Deletes the specified dashboard
        """
        return await self.__http_client.make_request(
            f"/api/config/v1/dashboards/{dashboard_id}", method="DELETE"
        )


class DashboardFilter(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.timeframe: str | None = raw_optional_str(raw_element, "timeframe")
        self.management_zone: EntityShortRepresentation | None = raw_optional_object(
            raw_element,
            "managementZone",
            lambda value: EntityShortRepresentation(self._http_client, None, value),
        )


class DashboardGenericTagFilter(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.display_name: str | None = raw_optional_str(raw_element, "displayName")
        self.entity_types: list[str] = raw_required_str_list(raw_element, "entityTypes")
        self.suggestions_from_entity_type: str | None = raw_optional_str(
            raw_element, "suggestionsFromEntityType"
        )
        self.tag_key: str | None = raw_optional_str(raw_element, "tagKey")


class DynamicFilters(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.filters: list[str] = raw_required_str_list(raw_element, "filters")
        self.generic_tag_filters: list[DashboardGenericTagFilter] = (
            raw_required_object_list(
                raw_element,
                "genericTagFilters",
                lambda value: DashboardGenericTagFilter(self._http_client, None, value),
            )
        )


class DashboardMetadata(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.name: str = raw_required_str(raw_element, "name")
        self.shared: bool | None = raw_optional_bool(raw_element, "shared")
        self.owner: str = raw_required_str(raw_element, "owner")
        self.dashboard_filter: DashboardFilter | None = raw_optional_object(
            raw_element,
            "dashboardFilter",
            lambda value: DashboardFilter(self._http_client, None, value),
        )
        self.dynamic_filters: DynamicFilters | None = raw_optional_object(
            raw_element,
            "dynamicFilters",
            lambda value: DynamicFilters(self._http_client, None, value),
        )
        self.has_consistent_colors: bool | None = raw_optional_bool(
            raw_element, "hasConsistentColors"
        )
        self.tags: list[str] | None = raw_optional_str_list_or_none(raw_element, "tags")
        self.preset: bool | None = raw_optional_bool(raw_element, "preset")
        self.tiles_name_size: str | None = raw_optional_str(
            raw_element, "tilesNameSize"
        )


class Dashboard(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.id: str | None = raw_optional_str(raw_element, "id")
        self.dashboard_metadata: DashboardMetadata = raw_required_object(
            raw_element,
            "dashboardMetadata",
            lambda value: DashboardMetadata(self._http_client, None, value),
        )
        self.metadata: ConfigurationMetadata | None = raw_optional_object(
            raw_element,
            "metadata",
            lambda value: ConfigurationMetadata(self._http_client, None, value),
        )
        self.tiles: list[Tile] = raw_required_object_list(
            raw_element, "tiles", lambda value: Tile(self._http_client, None, value)
        )
        self.raw_json: dict[str, Any] = raw_element


class DashboardAnonymousAccess(DynatraceObject):
    def to_json(self) -> dict[str, Any]:
        return {
            "managementZoneIds": self.management_zone_ids,
            "urls": self.urls,
        }

    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.management_zone_ids: list[str] = raw_required_str_list(
            raw_element, "managementZoneIds"
        )
        self.urls: dict[str, str] | None = raw_optional_str_dict(raw_element, "urls")


class DashboardSharePermissions(DynatraceObject):
    def to_json(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "permission": self.permission,
            "type": self.type,
        }

    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.id: str | None = raw_optional_str(raw_element, "id")
        self.permission: str = raw_required_str(raw_element, "permission")
        self.type: str = raw_required_str(raw_element, "type")


class DashboardSharing(DynatraceObject):
    def to_json(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "id": self.id,
            "permissions": [permission.to_json() for permission in self.permissions],
            "preset": self.preset,
            "publicAccess": self.public_access.to_json(),
        }

    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.enabled: bool | None = raw_optional_bool(raw_element, "enabled")
        self.id: str = raw_required_str(raw_element, "id")
        self.permissions: list[DashboardSharePermissions] = raw_required_object_list(
            raw_element,
            "permissions",
            lambda value: DashboardSharePermissions(self._http_client, None, value),
        )
        self.preset: bool | None = raw_optional_bool(raw_element, "preset")
        self.public_access: DashboardAnonymousAccess = raw_required_object(
            raw_element,
            "publicAccess",
            lambda value: DashboardAnonymousAccess(self._http_client, None, value),
        )


class DashboardStub(DynatraceObject):
    async def delete(self) -> Response:
        """
        Deletes this dashboard
        """
        return await self._make_request(
            f"/api/config/v1/dashboards/{self.id}", method="DELETE"
        )

    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.created: int | None = raw_optional_int(raw_element, "created")
        self.id: str = raw_required_str(raw_element, "id")
        self.last_modified: int | None = raw_optional_int(raw_element, "lastModified")
        self.last_viewed: int | None = raw_optional_int(raw_element, "lastViewed")
        self.name: str | None = raw_optional_str(raw_element, "name")
        self.owner: str | None = raw_optional_str(raw_element, "owner")
        self.popularity: int | None = raw_optional_int(raw_element, "popularity")

    async def get_full_dashboard(self) -> Dashboard:
        """
        Gets the full dashboard for this stub
        """
        response = (
            await self._make_request(f"/api/config/v1/dashboards/{self.id}")
        ).json()
        return Dashboard(self._http_client, None, response)
