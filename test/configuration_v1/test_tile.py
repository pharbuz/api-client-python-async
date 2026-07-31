from dynatrace.configuration_v1.tile import (
    DataExplorerTile,
    MarkdownTile,
    Tile,
    TileBounds,
    TileFilter,
    TileType,
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
            "queries": [{"id": "A"}],
            "queriesSettings": {"resolution": "Inf"},
            "visualConfig": {"type": "GRAPH_CHART"},
        }
    )

    assert isinstance(tile, DataExplorerTile)
    assert tile.tile_type == TileType.DATA_EXPLORER
    assert tile.custom_name == "Latency"
    assert tile.metric_expressions == ["builtin:service.response.time"]
    assert tile.queries == [{"id": "A"}]
    assert tile.queries_settings == {"resolution": "Inf"}
    assert tile.visual_config == {"type": "GRAPH_CHART"}
