from dynatrace.configuration_v1.tile import (
    CustomChartingTile,
    CustomFilterConfig,
    DataExplorerQuery,
    DataExplorerQuerySettings,
    DataExplorerTile,
    MarkdownTile,
    Tile,
    TileBounds,
    TileFilter,
    TileType,
    UserSessionQueryTile,
    UserSessionQueryTileConfiguration,
    VisualizationConfiguration,
)
from dynatrace.environment_v2.monitored_entities import EntityShortRepresentation


def test_tile_builds_bounds_and_tile_filter_objects() -> None:
    tile = Tile(
        raw_element={
            "name": "Markdown",
            "tileType": "MARKDOWN",
            "configured": True,
            "bounds": {"top": 1, "left": 2, "width": 3, "height": 4},
            "tileFilter": {
                "timeframe": "now-2h",
                "managementZone": {
                    "id": "123",
                    "name": "Production",
                    "description": "Production zone",
                },
            },
            "markdown": "# Status",
        }
    )

    assert isinstance(tile, MarkdownTile)
    assert tile.tile_type == TileType.MARKDOWN
    assert isinstance(tile.bounds, TileBounds)
    assert tile.bounds.top == 1
    assert tile.bounds.left == 2
    assert tile.bounds.width == 3
    assert tile.bounds.height == 4
    assert isinstance(tile.tile_filter, TileFilter)
    assert tile.tile_filter.timeframe == "now-2h"
    assert isinstance(tile.tile_filter.management_zone, EntityShortRepresentation)
    assert tile.tile_filter.management_zone.id == "123"
    assert tile.markdown == "# Status"


def test_tile_uses_openapi_discriminator_for_specialized_tile() -> None:
    tile = Tile(
        raw_element={
            "name": "Explorer",
            "tileType": "DATA_EXPLORER",
            "bounds": {"top": 0, "left": 0, "width": 304, "height": 152},
            "customName": "Latency",
            "metricExpressions": ["builtin:service.response.time"],
            "queries": [
                {
                    "enabled": True,
                    "filterBy": {"filterType": "NAME", "filter": "frontend"},
                    "id": "A",
                    "metric": "builtin:service.response.time",
                    "spaceAggregation": "AVG",
                    "splitBy": ["dt.entity.service"],
                    "timeAggregation": "AVG",
                }
            ],
            "queriesSettings": {"resolution": "Inf"},
            "visualConfig": {
                "rules": [{"matcher": "A", "properties": {"color": "BLUE"}}],
                "type": "GRAPH_CHART",
            },
        }
    )

    assert isinstance(tile, DataExplorerTile)
    assert tile.tile_type == TileType.DATA_EXPLORER
    assert tile.custom_name == "Latency"
    assert tile.metric_expressions == ["builtin:service.response.time"]
    assert tile.queries is not None
    assert isinstance(tile.queries[0], DataExplorerQuery)
    assert tile.queries[0].id == "A"
    assert tile.queries[0].filter_by is not None
    assert tile.queries[0].filter_by.filter_type == "NAME"
    assert isinstance(tile.queries_settings, DataExplorerQuerySettings)
    assert tile.queries_settings.resolution == "Inf"
    assert isinstance(tile.visual_config, VisualizationConfiguration)
    assert tile.visual_config.type == "GRAPH_CHART"
    assert tile.visual_config.rules is not None
    assert tile.visual_config.rules[0].properties is not None
    assert tile.visual_config.rules[0].properties.color == "BLUE"


def test_tile_builds_custom_charting_model() -> None:
    tile = Tile(
        raw_element={
            "name": "CPU",
            "tileType": "CUSTOM_CHARTING",
            "bounds": {"top": 0, "left": 0, "width": 304, "height": 152},
            "filterConfig": {
                "customName": "CPU",
                "defaultName": "Custom chart",
                "filtersPerEntityType": {},
                "type": "MIXED",
                "chartConfig": {
                    "resultMetadata": {
                        "builtin:host.cpu.usage": {"customColor": "#008cdb"}
                    },
                    "series": [
                        {
                            "aggregation": "AVG",
                            "dimensions": [
                                {"id": "dt.entity.host", "values": ["HOST-1"]}
                            ],
                            "entityType": "HOST",
                            "metric": "builtin:host.cpu.usage",
                            "type": "LINE",
                        }
                    ],
                    "type": "TIMESERIES",
                },
            },
        }
    )

    assert isinstance(tile, CustomChartingTile)
    assert isinstance(tile.filter_config, CustomFilterConfig)
    assert tile.filter_config.chart_config is not None
    assert tile.filter_config.chart_config.series is not None
    assert tile.filter_config.chart_config.series[0].metric == "builtin:host.cpu.usage"
    assert tile.filter_config.chart_config.result_metadata is not None
    assert (
        tile.filter_config.chart_config.result_metadata[
            "builtin:host.cpu.usage"
        ].custom_color
        == "#008cdb"
    )


def test_tile_builds_user_session_query_configuration() -> None:
    tile = Tile(
        raw_element={
            "name": "Sessions",
            "tileType": "DTAQL",
            "bounds": {"top": 0, "left": 0, "width": 304, "height": 152},
            "customName": "Sessions",
            "query": "SELECT * FROM usersession",
            "type": "TABLE",
            "visualizationConfig": {"hasAxisBucketing": True},
        }
    )

    assert isinstance(tile, UserSessionQueryTile)
    assert isinstance(tile.visualization_config, UserSessionQueryTileConfiguration)
    assert tile.visualization_config.has_axis_bucketing
