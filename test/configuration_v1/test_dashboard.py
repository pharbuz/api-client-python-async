from dynatrace.configuration_v1.dashboard import (
    Dashboard,
    DashboardAnonymousAccess,
    DashboardGenericTagFilter,
    DashboardMetadata,
    DashboardSharePermissions,
    DashboardSharing,
    DashboardStub,
    DynamicFilters,
)
from dynatrace.configuration_v1.tile import MarkdownTile


def test_dashboard_metadata_parses_dynamic_filters() -> None:
    metadata = DashboardMetadata(
        raw_element={
            "name": "Example Dashboard",
            "owner": "Example Owner",
            "shared": True,
            "dashboardFilter": {"timeframe": "l_72_HOURS"},
            "dynamicFilters": {
                "filters": ["SERVICE_TYPE", "HOST_TAG_KEY:env"],
                "genericTagFilters": [
                    {
                        "displayName": "Environment",
                        "entityTypes": ["HOST", "SERVICE"],
                        "suggestionsFromEntityType": "HOST",
                        "tagKey": "env",
                    }
                ],
            },
            "hasConsistentColors": True,
            "tags": ["team-a"],
            "preset": False,
            "tilesNameSize": "medium",
        }
    )

    assert metadata.name == "Example Dashboard"
    assert metadata.owner == "Example Owner"
    assert metadata.shared is True
    assert metadata.dashboard_filter is not None
    assert metadata.dashboard_filter.timeframe == "l_72_HOURS"
    assert isinstance(metadata.dynamic_filters, DynamicFilters)
    assert metadata.dynamic_filters.filters == ["SERVICE_TYPE", "HOST_TAG_KEY:env"]
    assert len(metadata.dynamic_filters.generic_tag_filters) == 1

    generic_filter = metadata.dynamic_filters.generic_tag_filters[0]
    assert isinstance(generic_filter, DashboardGenericTagFilter)
    assert generic_filter.display_name == "Environment"
    assert generic_filter.entity_types == ["HOST", "SERVICE"]
    assert generic_filter.suggestions_from_entity_type == "HOST"
    assert generic_filter.tag_key == "env"
    assert metadata.has_consistent_colors is True
    assert metadata.tags == ["team-a"]
    assert metadata.preset is False
    assert metadata.tiles_name_size == "medium"


def test_dashboard_parses_required_openapi_models() -> None:
    dashboard = Dashboard(
        raw_element={
            "id": "dashboard-id",
            "dashboardMetadata": {
                "name": "Example Dashboard",
                "owner": "Example Owner",
            },
            "metadata": {
                "clusterVersion": "1.0.0",
                "configurationVersions": [1],
            },
            "tiles": [
                {
                    "name": "Notes",
                    "tileType": "MARKDOWN",
                    "bounds": {"top": 0, "left": 0, "width": 304, "height": 152},
                    "markdown": "# Notes",
                }
            ],
        }
    )

    assert dashboard.id == "dashboard-id"
    assert dashboard.dashboard_metadata.name == "Example Dashboard"
    assert dashboard.metadata is not None
    assert dashboard.metadata.cluster_version == "1.0.0"
    assert len(dashboard.tiles) == 1
    assert isinstance(dashboard.tiles[0], MarkdownTile)


def test_dashboard_stub_parses_openapi_fields() -> None:
    stub = DashboardStub(
        raw_element={
            "created": 1776772474839,
            "id": "dashboard-id",
            "lastModified": 1776858899692,
            "lastViewed": 1776945274839,
            "name": "Home dashboard",
            "owner": "admin",
            "popularity": 5,
        }
    )

    assert stub.created == 1776772474839
    assert stub.id == "dashboard-id"
    assert stub.last_modified == 1776858899692
    assert stub.last_viewed == 1776945274839
    assert stub.name == "Home dashboard"
    assert stub.owner == "admin"
    assert stub.popularity == 5


def test_dashboard_sharing_parses_openapi_models() -> None:
    sharing = DashboardSharing(
        raw_element={
            "enabled": True,
            "id": "dashboard-id",
            "permissions": [
                {"permission": "VIEW", "type": "ALL"},
                {"id": "group-id", "permission": "EDIT", "type": "GROUP"},
            ],
            "preset": False,
            "publicAccess": {
                "managementZoneIds": ["default"],
                "urls": {"default": "https://example.com/dashboard"},
            },
        }
    )

    assert sharing.enabled is True
    assert sharing.id == "dashboard-id"
    assert len(sharing.permissions) == 2
    assert isinstance(sharing.permissions[0], DashboardSharePermissions)
    assert sharing.permissions[1].id == "group-id"
    assert isinstance(sharing.public_access, DashboardAnonymousAccess)
    assert sharing.public_access.management_zone_ids == ["default"]
    assert sharing.public_access.urls == {"default": "https://example.com/dashboard"}
    assert sharing.to_json()["publicAccess"]["managementZoneIds"] == ["default"]
