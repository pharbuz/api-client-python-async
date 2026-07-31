from dynatrace.configuration_v1.dashboard import (
    DashboardGenericTagFilter,
    DashboardMetadata,
    DynamicFilters,
)


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
