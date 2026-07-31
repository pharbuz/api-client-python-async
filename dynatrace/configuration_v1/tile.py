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

from collections.abc import Callable
from enum import Enum
from typing import Any, TypeVar

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.environment_v2.monitored_entities import EntityShortRepresentation
from dynatrace.http_client import HttpClient
from dynatrace.utils import raw_optional_bool, raw_optional_int, raw_optional_str

T = TypeVar("T")


class TileType(Enum):
    APPLICATION = "APPLICATION"
    APPLICATIONS = "APPLICATIONS"
    APPLICATIONS_MOST_ACTIVE = "APPLICATIONS_MOST_ACTIVE"
    APPLICATION_METHOD = "APPLICATION_METHOD"
    APPLICATION_WORLDMAP = "APPLICATION_WORLDMAP"
    AWS = "AWS"
    BOUNCE_RATE = "BOUNCE_RATE"
    CUSTOM_APPLICATION = "CUSTOM_APPLICATION"
    CUSTOM_CHARTING = "CUSTOM_CHARTING"
    DATABASE = "DATABASE"
    DATABASES_OVERVIEW = "DATABASES_OVERVIEW"
    DATA_EXPLORER = "DATA_EXPLORER"
    DCRUM_SERVICES = "DCRUM_SERVICES"
    DEM_KEY_USER_ACTION = "DEM_KEY_USER_ACTION"
    DEVICE_APPLICATION_METHOD = "DEVICE_APPLICATION_METHOD"
    DOCKER = "DOCKER"
    DTAQL = "DTAQL"
    HEADER = "HEADER"
    HOST = "HOST"
    HOSTS = "HOSTS"
    IMAGE = "IMAGE"
    LOG_ANALYTICS = "LOG_ANALYTICS"
    MARKDOWN = "MARKDOWN"
    MOBILE_APPLICATION = "MOBILE_APPLICATION"
    NETWORK = "NETWORK"
    NETWORK_MEDIUM = "NETWORK_MEDIUM"
    OPENSTACK = "OPENSTACK"
    OPENSTACK_AV_ZONE = "OPENSTACK_AV_ZONE"
    OPENSTACK_PROJECT = "OPENSTACK_PROJECT"
    OPEN_PROBLEMS = "OPEN_PROBLEMS"
    PROCESS_GROUPS_ONE = "PROCESS_GROUPS_ONE"
    PURE_MODEL = "PURE_MODEL"
    RESOURCES = "RESOURCES"
    SCALABLE_LIST = "SCALABLE_LIST"
    SERVICES = "SERVICES"
    SERVICE_VERSATILE = "SERVICE_VERSATILE"
    SESSION_METRICS = "SESSION_METRICS"
    SLO = "SLO"
    SYNTHETIC_HTTP_MONITOR = "SYNTHETIC_HTTP_MONITOR"
    SYNTHETIC_SINGLE_EXT_TEST = "SYNTHETIC_SINGLE_EXT_TEST"
    SYNTHETIC_SINGLE_WEBCHECK = "SYNTHETIC_SINGLE_WEBCHECK"
    SYNTHETIC_TESTS = "SYNTHETIC_TESTS"
    THIRD_PARTY_MOST_ACTIVE = "THIRD_PARTY_MOST_ACTIVE"
    UEM_ACTIVE_SESSIONS = "UEM_ACTIVE_SESSIONS"
    UEM_CONVERSIONS_OVERALL = "UEM_CONVERSIONS_OVERALL"
    UEM_CONVERSIONS_PER_GOAL = "UEM_CONVERSIONS_PER_GOAL"
    UEM_JSERRORS_OVERALL = "UEM_JSERRORS_OVERALL"
    UEM_KEY_USER_ACTIONS = "UEM_KEY_USER_ACTIONS"
    USERS = "USERS"
    VIRTUALIZATION = "VIRTUALIZATION"


class TileBounds(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.height: int | None = raw_optional_int(raw_element, "height")
        self.left: int | None = raw_optional_int(raw_element, "left")
        self.top: int | None = raw_optional_int(raw_element, "top")
        self.width: int | None = raw_optional_int(raw_element, "width")


class TileFilter(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        management_zone = raw_element.get("managementZone")
        self.management_zone: EntityShortRepresentation | None = (
            EntityShortRepresentation(self._http_client, None, management_zone)
            if isinstance(management_zone, dict)
            else None
        )
        self.timeframe: str | None = raw_optional_str(raw_element, "timeframe")


class Tile(DynatraceObject):
    def __new__(
        cls,
        http_client: HttpClient | None = None,
        headers: dict[str, str] | None = None,
        raw_element: dict[str, Any] | None = None,
    ) -> "Tile":
        if cls is Tile and raw_element is not None:
            tile_type = raw_element.get("tileType")
            if isinstance(tile_type, str):
                tile_class = _TILE_CLASS_BY_TYPE.get(tile_type)
                if tile_class is not None:
                    return super().__new__(tile_class)
        return super().__new__(cls)

    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.name: str | None = raw_optional_str(raw_element, "name")
        raw_tile_type = raw_optional_str(raw_element, "tileType")
        self.tile_type: TileType | str | None = (
            TileType(raw_tile_type)
            if raw_tile_type in TileType._value2member_map_
            else raw_tile_type
        )
        self.configured: bool | None = raw_optional_bool(raw_element, "configured")
        self.is_auto_refresh_disabled: bool | None = raw_optional_bool(
            raw_element, "isAutoRefreshDisabled"
        )
        self.name_size: str | None = raw_optional_str(raw_element, "nameSize")
        self.bounds: TileBounds | None = _optional_object(
            raw_element, "bounds", lambda value: TileBounds(raw_element=value)
        )
        self.tile_filter: TileFilter | None = _optional_object(
            raw_element,
            "tileFilter",
            lambda value: TileFilter(self._http_client, None, value),
        )


class AssignedEntitiesTile(Tile):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        super()._create_from_raw_data(raw_element)
        self.assigned_entities: list[str] | None = _optional_str_list(
            raw_element, "assignedEntities"
        )


class AssignedEntitiesWithMetricTile(AssignedEntitiesTile):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        super()._create_from_raw_data(raw_element)
        self.metric: str | None = raw_optional_str(raw_element, "metric")


class CustomChartingTile(Tile):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        super()._create_from_raw_data(raw_element)
        self.filter_config: dict[str, Any] | None = _optional_dict(
            raw_element, "filterConfig"
        )


class DataExplorerTile(Tile):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        super()._create_from_raw_data(raw_element)
        self.custom_name: str | None = raw_optional_str(raw_element, "customName")
        self.metric_expressions: list[str] | None = _optional_str_list(
            raw_element, "metricExpressions"
        )
        self.queries: list[dict[str, Any]] | None = _optional_dict_list(
            raw_element, "queries"
        )
        self.queries_settings: dict[str, Any] | None = _optional_dict(
            raw_element, "queriesSettings"
        )
        self.visual_config: dict[str, Any] | None = _optional_dict(
            raw_element, "visualConfig"
        )


class FilterableEntityTile(Tile):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        super()._create_from_raw_data(raw_element)
        self.chart_visible: bool | None = raw_optional_bool(raw_element, "chartVisible")
        self.filter_config: dict[str, Any] | None = _optional_dict(
            raw_element, "filterConfig"
        )


class ImageTile(Tile):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        super()._create_from_raw_data(raw_element)
        self.image: str | None = raw_optional_str(raw_element, "image")


class MarkdownTile(Tile):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        super()._create_from_raw_data(raw_element)
        self.markdown: str | None = raw_optional_str(raw_element, "markdown")


class ProblemTile(Tile):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        super()._create_from_raw_data(raw_element)
        self.entity_selector: str | None = raw_optional_str(
            raw_element, "entitySelector"
        )
        self.problem_selector: str | None = raw_optional_str(
            raw_element, "problemSelector"
        )
        self.use_background_color: bool | None = raw_optional_bool(
            raw_element, "useBackgroundColor"
        )


class ScalableListTile(Tile):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        super()._create_from_raw_data(raw_element)
        self.chart_visible: bool | None = raw_optional_bool(raw_element, "chartVisible")
        self.custom_filter_id: str | None = raw_optional_str(
            raw_element, "customFilterId"
        )
        self.entity_specific_tile_type: TileType | str | None = _optional_tile_type(
            raw_element, "entitySpecificTileType"
        )


class SyntheticSingleWebcheckTile(AssignedEntitiesTile):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        super()._create_from_raw_data(raw_element)
        self.exclude_maintenance_windows: bool | None = raw_optional_bool(
            raw_element, "excludeMaintenanceWindows"
        )


class UserSessionQueryTile(Tile):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        super()._create_from_raw_data(raw_element)
        self.custom_name: str | None = raw_optional_str(raw_element, "customName")
        self.limit: int | None = raw_optional_int(raw_element, "limit")
        self.query: str | None = raw_optional_str(raw_element, "query")
        self.time_frame_shift: str | None = raw_optional_str(
            raw_element, "timeFrameShift"
        )
        self.type: str | None = raw_optional_str(raw_element, "type")
        self.visualization_config: dict[str, Any] | None = _optional_dict(
            raw_element, "visualizationConfig"
        )


def _optional_object(
    raw_element: dict[str, Any], key: str, factory: Callable[[dict[str, Any]], T]
) -> T | None:
    value = raw_element.get(key)
    if value is None:
        return None
    if not isinstance(value, dict):
        raise TypeError(f"expected raw field {key!r} to be object")
    return factory(value)


def _optional_dict(raw_element: dict[str, Any], key: str) -> dict[str, Any] | None:
    value = raw_element.get(key)
    if value is None:
        return None
    if not isinstance(value, dict):
        raise TypeError(f"expected raw field {key!r} to be object")
    return value


def _optional_str_list(raw_element: dict[str, Any], key: str) -> list[str] | None:
    value = raw_element.get(key)
    if value is None:
        return None
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise TypeError(f"expected raw field {key!r} to be list[str]")
    return value


def _optional_dict_list(
    raw_element: dict[str, Any], key: str
) -> list[dict[str, Any]] | None:
    value = raw_element.get(key)
    if value is None:
        return None
    if not isinstance(value, list) or not all(isinstance(item, dict) for item in value):
        raise TypeError(f"expected raw field {key!r} to be list[object]")
    return value


def _optional_tile_type(raw_element: dict[str, Any], key: str) -> TileType | str | None:
    raw_tile_type = raw_optional_str(raw_element, key)
    if raw_tile_type is None:
        return None
    if raw_tile_type in TileType._value2member_map_:
        return TileType(raw_tile_type)
    return raw_tile_type


_FILTERABLE_ENTITY_TILE_TYPES = {
    TileType.HOSTS.value,
    TileType.APPLICATIONS.value,
    TileType.SERVICES.value,
    TileType.DATABASES_OVERVIEW.value,
    TileType.SYNTHETIC_TESTS.value,
}

_ASSIGNED_ENTITIES_WITH_METRIC_TILE_TYPES = {
    TileType.APPLICATION_WORLDMAP.value,
    TileType.RESOURCES.value,
    TileType.THIRD_PARTY_MOST_ACTIVE.value,
    TileType.UEM_CONVERSIONS_PER_GOAL.value,
    TileType.HOST.value,
    TileType.PROCESS_GROUPS_ONE.value,
    TileType.SLO.value,
}

_ASSIGNED_ENTITIES_TILE_TYPES = {
    TileType.APPLICATION.value,
    TileType.VIRTUALIZATION.value,
    TileType.AWS.value,
    TileType.SERVICE_VERSATILE.value,
    TileType.SESSION_METRICS.value,
    TileType.USERS.value,
    TileType.UEM_KEY_USER_ACTIONS.value,
    TileType.BOUNCE_RATE.value,
    TileType.UEM_CONVERSIONS_OVERALL.value,
    TileType.UEM_JSERRORS_OVERALL.value,
    TileType.MOBILE_APPLICATION.value,
    TileType.SYNTHETIC_SINGLE_EXT_TEST.value,
    TileType.SYNTHETIC_HTTP_MONITOR.value,
    TileType.DATABASE.value,
    TileType.CUSTOM_APPLICATION.value,
    TileType.APPLICATION_METHOD.value,
    TileType.LOG_ANALYTICS.value,
    TileType.OPENSTACK.value,
    TileType.OPENSTACK_PROJECT.value,
    TileType.OPENSTACK_AV_ZONE.value,
    TileType.DEVICE_APPLICATION_METHOD.value,
    TileType.DEM_KEY_USER_ACTION.value,
}

_TILE_CLASS_BY_TYPE: dict[str, type[Tile]] = {
    TileType.DATA_EXPLORER.value: DataExplorerTile,
    TileType.CUSTOM_CHARTING.value: CustomChartingTile,
    TileType.DTAQL.value: UserSessionQueryTile,
    TileType.MARKDOWN.value: MarkdownTile,
    TileType.IMAGE.value: ImageTile,
    TileType.SYNTHETIC_SINGLE_WEBCHECK.value: SyntheticSingleWebcheckTile,
    TileType.SCALABLE_LIST.value: ScalableListTile,
    TileType.OPEN_PROBLEMS.value: ProblemTile,
    **{tile_type: FilterableEntityTile for tile_type in _FILTERABLE_ENTITY_TILE_TYPES},
    **{
        tile_type: AssignedEntitiesWithMetricTile
        for tile_type in _ASSIGNED_ENTITIES_WITH_METRIC_TILE_TYPES
    },
    **{tile_type: AssignedEntitiesTile for tile_type in _ASSIGNED_ENTITIES_TILE_TYPES},
}
