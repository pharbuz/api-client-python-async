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
from dynatrace.environment_v2.monitored_entities import EntityShortRepresentation
from dynatrace.http_client import HttpClient
from dynatrace.utils import (
    raw_optional_bool,
    raw_optional_dict,
    raw_optional_float,
    raw_optional_float_dict,
    raw_optional_int,
    raw_optional_object,
    raw_optional_object_dict,
    raw_optional_object_list,
    raw_optional_str,
    raw_optional_str_list_or_none,
)


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
        self.bounds: TileBounds | None = raw_optional_object(
            raw_element, "bounds", lambda value: TileBounds(raw_element=value)
        )
        self.tile_filter: TileFilter | None = raw_optional_object(
            raw_element,
            "tileFilter",
            lambda value: TileFilter(self._http_client, None, value),
        )


class CustomChartingItemMetadataConfig(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.custom_color: str | None = raw_optional_str(raw_element, "customColor")
        self.last_modified: int | None = raw_optional_int(raw_element, "lastModified")


class CustomFilterChartSeriesDimensionConfig(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.entity_dimension: bool | None = raw_optional_bool(
            raw_element, "entityDimension"
        )
        self.id: str | None = raw_optional_str(raw_element, "id")
        self.name: str | None = raw_optional_str(raw_element, "name")
        self.values: list[str] | None = raw_optional_str_list_or_none(
            raw_element, "values"
        )


class CustomFilterChartSeriesConfig(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.aggregation: str | None = raw_optional_str(raw_element, "aggregation")
        self.aggregation_rate: str | None = raw_optional_str(
            raw_element, "aggregationRate"
        )
        self.dimensions: list[CustomFilterChartSeriesDimensionConfig] | None = (
            raw_optional_object_list(
                raw_element,
                "dimensions",
                lambda value: CustomFilterChartSeriesDimensionConfig(raw_element=value),
            )
        )
        self.entity_type: str | None = raw_optional_str(raw_element, "entityType")
        self.metric: str | None = raw_optional_str(raw_element, "metric")
        self.percentile: int | None = raw_optional_int(raw_element, "percentile")
        self.sort_ascending: bool | None = raw_optional_bool(
            raw_element, "sortAscending"
        )
        self.sort_column: bool | None = raw_optional_bool(raw_element, "sortColumn")
        self.type: str | None = raw_optional_str(raw_element, "type")


class CustomFilterChartConfig(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.axis_limits: dict[str, float] | None = raw_optional_float_dict(
            raw_element, "axisLimits"
        )
        self.left_axis_custom_unit: str | None = raw_optional_str(
            raw_element, "leftAxisCustomUnit"
        )
        self.legend_shown: bool | None = raw_optional_bool(raw_element, "legendShown")
        self.result_metadata: dict[str, CustomChartingItemMetadataConfig] | None = (
            raw_optional_object_dict(
                raw_element,
                "resultMetadata",
                lambda value: CustomChartingItemMetadataConfig(raw_element=value),
            )
        )
        self.right_axis_custom_unit: str | None = raw_optional_str(
            raw_element, "rightAxisCustomUnit"
        )
        self.series: list[CustomFilterChartSeriesConfig] | None = (
            raw_optional_object_list(
                raw_element,
                "series",
                lambda value: CustomFilterChartSeriesConfig(raw_element=value),
            )
        )
        self.type: str | None = raw_optional_str(raw_element, "type")


class CustomFilterConfig(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.chart_config: CustomFilterChartConfig | None = raw_optional_object(
            raw_element,
            "chartConfig",
            lambda value: CustomFilterChartConfig(raw_element=value),
        )
        self.custom_name: str | None = raw_optional_str(raw_element, "customName")
        self.default_name: str | None = raw_optional_str(raw_element, "defaultName")
        self.filters_per_entity_type: dict[str, Any] | None = raw_optional_dict(
            raw_element, "filtersPerEntityType"
        )
        self.type: str | None = raw_optional_str(raw_element, "type")


class DexpFilterCriterion(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.evaluator: str | None = raw_optional_str(raw_element, "evaluator")
        self.match_exactly: bool | None = raw_optional_bool(raw_element, "matchExactly")
        self.value: str | None = raw_optional_str(raw_element, "value")


class DexpFilterRelationship(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.id: str | None = raw_optional_str(raw_element, "id")
        self.target_entity: str | None = raw_optional_str(raw_element, "targetEntity")
        self.type: str | None = raw_optional_str(raw_element, "type")


class DataExplorerFilter(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.criteria: list[DexpFilterCriterion] | None = raw_optional_object_list(
            raw_element,
            "criteria",
            lambda value: DexpFilterCriterion(raw_element=value),
        )
        self.entity_attribute: str | None = raw_optional_str(
            raw_element, "entityAttribute"
        )
        self.filter: str | None = raw_optional_str(raw_element, "filter")
        self.filter_operator: str | None = raw_optional_str(
            raw_element, "filterOperator"
        )
        self.filter_type: str | None = raw_optional_str(raw_element, "filterType")
        self.global_entity: str | None = raw_optional_str(raw_element, "globalEntity")
        self.nested_filters: list[DataExplorerFilter] | None = raw_optional_object_list(
            raw_element,
            "nestedFilters",
            lambda value: DataExplorerFilter(raw_element=value),
        )
        self.relationship: DexpFilterRelationship | None = raw_optional_object(
            raw_element,
            "relationship",
            lambda value: DexpFilterRelationship(raw_element=value),
        )


class DataExplorerTimeShift(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.factor: int | None = raw_optional_int(raw_element, "factor")
        self.unit: str | None = raw_optional_str(raw_element, "unit")


class DataExplorerQuery(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.default_value: float | None = raw_optional_float(
            raw_element, "defaultValue"
        )
        self.enabled: bool | None = raw_optional_bool(raw_element, "enabled")
        self.filter_by: DataExplorerFilter | None = raw_optional_object(
            raw_element, "filterBy", lambda value: DataExplorerFilter(raw_element=value)
        )
        self.fold_transformation: str | None = raw_optional_str(
            raw_element, "foldTransformation"
        )
        self.generated_metric_selector: str | None = raw_optional_str(
            raw_element, "generatedMetricSelector"
        )
        self.histogram: bool | None = raw_optional_bool(raw_element, "histogram")
        self.id: str | None = raw_optional_str(raw_element, "id")
        self.limit: int | None = raw_optional_int(raw_element, "limit")
        self.metric: str | None = raw_optional_str(raw_element, "metric")
        self.metric_selector: str | None = raw_optional_str(
            raw_element, "metricSelector"
        )
        self.rate: str | None = raw_optional_str(raw_element, "rate")
        self.sort_by: str | None = raw_optional_str(raw_element, "sortBy")
        self.sort_by_dimension: str | None = raw_optional_str(
            raw_element, "sortByDimension"
        )
        self.space_aggregation: str | None = raw_optional_str(
            raw_element, "spaceAggregation"
        )
        self.split_by: list[str] | None = raw_optional_str_list_or_none(
            raw_element, "splitBy"
        )
        self.time_aggregation: str | None = raw_optional_str(
            raw_element, "timeAggregation"
        )
        self.time_shift: DataExplorerTimeShift | None = raw_optional_object(
            raw_element,
            "timeShift",
            lambda value: DataExplorerTimeShift(raw_element=value),
        )


class DataExplorerQuerySettings(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.fold_aggregation: str | None = raw_optional_str(
            raw_element, "foldAggregation"
        )
        self.fold_transformation: str | None = raw_optional_str(
            raw_element, "foldTransformation"
        )
        self.global_limit_query_id: str | None = raw_optional_str(
            raw_element, "globalLimitQueryId"
        )
        self.resolution: str | None = raw_optional_str(raw_element, "resolution")


class Axis(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.display_name: str | None = raw_optional_str(raw_element, "displayName")
        self.visible: bool | None = raw_optional_bool(raw_element, "visible")


class YAxis(Axis):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        super()._create_from_raw_data(raw_element)
        self.default_axis: bool | None = raw_optional_bool(raw_element, "defaultAxis")
        self.max: str | None = raw_optional_str(raw_element, "max")
        self.min: str | None = raw_optional_str(raw_element, "min")
        self.position: str | None = raw_optional_str(raw_element, "position")
        self.query_ids: list[str] | None = raw_optional_str_list_or_none(
            raw_element, "queryIds"
        )


class Axes(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.x_axis: Axis | None = raw_optional_object(
            raw_element, "xAxis", lambda value: Axis(raw_element=value)
        )
        self.y_axes: list[YAxis] | None = raw_optional_object_list(
            raw_element, "yAxes", lambda value: YAxis(raw_element=value)
        )


class VisualizationThresholdRule(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.color: str | None = raw_optional_str(raw_element, "color")
        self.value: float | None = raw_optional_float(raw_element, "value")


class VisualizationThreshold(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.axis_target: str | None = raw_optional_str(raw_element, "axisTarget")
        self.column_id: str | None = raw_optional_str(raw_element, "columnId")
        self.query_id: str | None = raw_optional_str(raw_element, "queryId")
        self.rules: list[VisualizationThresholdRule] | None = raw_optional_object_list(
            raw_element,
            "rules",
            lambda value: VisualizationThresholdRule(raw_element=value),
        )
        self.visible: bool | None = raw_optional_bool(raw_element, "visible")


class VisualizationGlobalProperties(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.has_trendline: bool | None = raw_optional_bool(raw_element, "hasTrendline")
        self.hide_legend: bool | None = raw_optional_bool(raw_element, "hideLegend")
        self.series_type: str | None = raw_optional_str(raw_element, "seriesType")
        self.theme: str | None = raw_optional_str(raw_element, "theme")
        self.threshold: VisualizationThreshold | None = raw_optional_object(
            raw_element,
            "threshold",
            lambda value: VisualizationThreshold(raw_element=value),
        )


class GraphChartSettings(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.connect_nulls: bool | None = raw_optional_bool(raw_element, "connectNulls")


class HeatmapSettings(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.show_labels: bool | None = raw_optional_bool(raw_element, "showLabels")
        self.x_axis_buckets: int | None = raw_optional_int(raw_element, "xAxisBuckets")
        self.y_axis: str | None = raw_optional_str(raw_element, "yAxis")
        self.y_axis_buckets: int | None = raw_optional_int(raw_element, "yAxisBuckets")


class HoneycombSettings(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.show_hive: bool | None = raw_optional_bool(raw_element, "showHive")
        self.show_labels: bool | None = raw_optional_bool(raw_element, "showLabels")
        self.show_legend: bool | None = raw_optional_bool(raw_element, "showLegend")


class VisualizationProperties(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.alias: str | None = raw_optional_str(raw_element, "alias")
        self.color: str | None = raw_optional_str(raw_element, "color")
        self.series_type: str | None = raw_optional_str(raw_element, "seriesType")


class VisualizationSerieOverride(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.color: str | None = raw_optional_str(raw_element, "color")
        self.name: str | None = raw_optional_str(raw_element, "name")


class VisualizationRule(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.matcher: str | None = raw_optional_str(raw_element, "matcher")
        self.properties: VisualizationProperties | None = raw_optional_object(
            raw_element,
            "properties",
            lambda value: VisualizationProperties(raw_element=value),
        )
        self.series_overrides: list[VisualizationSerieOverride] | None = (
            raw_optional_object_list(
                raw_element,
                "seriesOverrides",
                lambda value: VisualizationSerieOverride(raw_element=value),
            )
        )
        self.unit_transform: str | None = raw_optional_str(raw_element, "unitTransform")
        self.value_format: str | None = raw_optional_str(raw_element, "valueFormat")


class SingleValueSettings(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.link_tile_color_to_threshold: bool | None = raw_optional_bool(
            raw_element, "linkTileColorToThreshold"
        )
        self.show_spark_line: bool | None = raw_optional_bool(
            raw_element, "showSparkLine"
        )
        self.show_trend: bool | None = raw_optional_bool(raw_element, "showTrend")


class TableSettings(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.hidden_columns: list[str] | None = raw_optional_str_list_or_none(
            raw_element, "hiddenColumns"
        )
        self.is_threshold_background_applied_to_cell: bool | None = raw_optional_bool(
            raw_element, "isThresholdBackgroundAppliedToCell"
        )


class VisualizationConfiguration(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.axes: Axes | None = raw_optional_object(
            raw_element, "axes", lambda value: Axes(raw_element=value)
        )
        self.global_properties: VisualizationGlobalProperties | None = (
            raw_optional_object(
                raw_element,
                "global",
                lambda value: VisualizationGlobalProperties(raw_element=value),
            )
        )
        self.graph_chart_settings: GraphChartSettings | None = raw_optional_object(
            raw_element,
            "graphChartSettings",
            lambda value: GraphChartSettings(raw_element=value),
        )
        self.heatmap_settings: HeatmapSettings | None = raw_optional_object(
            raw_element,
            "heatmapSettings",
            lambda value: HeatmapSettings(raw_element=value),
        )
        self.honeycomb_settings: HoneycombSettings | None = raw_optional_object(
            raw_element,
            "honeycombSettings",
            lambda value: HoneycombSettings(raw_element=value),
        )
        self.rules: list[VisualizationRule] | None = raw_optional_object_list(
            raw_element, "rules", lambda value: VisualizationRule(raw_element=value)
        )
        self.single_value_settings: SingleValueSettings | None = raw_optional_object(
            raw_element,
            "singleValueSettings",
            lambda value: SingleValueSettings(raw_element=value),
        )
        self.table_settings: TableSettings | None = raw_optional_object(
            raw_element,
            "tableSettings",
            lambda value: TableSettings(raw_element=value),
        )
        self.thresholds: list[VisualizationThreshold] | None = raw_optional_object_list(
            raw_element,
            "thresholds",
            lambda value: VisualizationThreshold(raw_element=value),
        )
        self.type: str | None = raw_optional_str(raw_element, "type")


class UserSessionQueryTileConfiguration(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.has_axis_bucketing: bool | None = raw_optional_bool(
            raw_element, "hasAxisBucketing"
        )


class AssignedEntitiesTile(Tile):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        super()._create_from_raw_data(raw_element)
        self.assigned_entities: list[str] | None = raw_optional_str_list_or_none(
            raw_element, "assignedEntities"
        )


class AssignedEntitiesWithMetricTile(AssignedEntitiesTile):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        super()._create_from_raw_data(raw_element)
        self.metric: str | None = raw_optional_str(raw_element, "metric")


class CustomChartingTile(Tile):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        super()._create_from_raw_data(raw_element)
        self.filter_config: CustomFilterConfig | None = raw_optional_object(
            raw_element,
            "filterConfig",
            lambda value: CustomFilterConfig(raw_element=value),
        )


class DataExplorerTile(Tile):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        super()._create_from_raw_data(raw_element)
        self.custom_name: str | None = raw_optional_str(raw_element, "customName")
        self.metric_expressions: list[str] | None = raw_optional_str_list_or_none(
            raw_element, "metricExpressions"
        )
        self.queries: list[DataExplorerQuery] | None = raw_optional_object_list(
            raw_element, "queries", lambda value: DataExplorerQuery(raw_element=value)
        )
        self.queries_settings: DataExplorerQuerySettings | None = raw_optional_object(
            raw_element,
            "queriesSettings",
            lambda value: DataExplorerQuerySettings(raw_element=value),
        )
        self.visual_config: VisualizationConfiguration | None = raw_optional_object(
            raw_element,
            "visualConfig",
            lambda value: VisualizationConfiguration(raw_element=value),
        )


class FilterableEntityTile(Tile):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        super()._create_from_raw_data(raw_element)
        self.chart_visible: bool | None = raw_optional_bool(raw_element, "chartVisible")
        self.filter_config: dict[str, Any] | None = raw_optional_dict(
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
        self.visualization_config: UserSessionQueryTileConfiguration | None = (
            raw_optional_object(
                raw_element,
                "visualizationConfig",
                lambda value: UserSessionQueryTileConfiguration(raw_element=value),
            )
        )


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
