from dynatrace import DynatraceAsync
from dynatrace.configuration_v1.alerting_profiles import (
    AlertingCustomEventFilter,
    AlertingCustomTextFilter,
    AlertingEventTypeFilter,
    AlertingPredefinedEvent,
    AlertingPredefinedEventFilter,
    AlertingProfile,
    AlertingProfileSeverityRule,
    AlertingProfileStub,
    AlertingProfileTagFilter,
    SeverityLevel,
    TagFilterIncludeMode,
)
from dynatrace.configuration_v1.schemas import (
    ConfigurationMetadata,
    StringComparisonOperator,
)
from dynatrace.environment_v2.custom_tags import METag
from dynatrace.environment_v2.monitored_entities import EntityShortRepresentation
from dynatrace.pagination import PaginatedList
from test.async_utils import collect

ID = "b1f379d9-98b4-4efe-be38-0289609c9295"
NAME = "deployment_change_autoremediation"


async def test_list(dt: DynatraceAsync):
    alert_profiles = await dt.alerting_profiles.list()
    assert isinstance(alert_profiles, PaginatedList)

    list_alert_profiles = await collect(alert_profiles)
    assert len(list_alert_profiles) == 6

    first = list_alert_profiles[0]
    assert isinstance(first, AlertingProfileStub)

    assert first.id == ID
    assert first.name == NAME


async def test_get_full_configuration(dt: DynatraceAsync):
    alert_profiles = await dt.alerting_profiles.list()
    list_alert_profiles = await collect(alert_profiles)
    first = list_alert_profiles[0]

    full = await first.get_full_configuration()
    assert isinstance(full, AlertingProfile)
    assert full.id == ID
    assert full.display_name == NAME
    assert isinstance(full.rules, list)
    assert isinstance(full.rules[0], AlertingProfileSeverityRule)


async def test_get(dt: DynatraceAsync):
    ap = await dt.alerting_profiles.get(profile_id=ID)

    # type checks
    assert isinstance(ap, AlertingProfile)
    assert isinstance(ap.metadata, ConfigurationMetadata)
    assert isinstance(ap.id, str)
    assert isinstance(ap.display_name, str)
    assert isinstance(ap.rules, list)
    assert all(isinstance(rule, AlertingProfileSeverityRule) for rule in ap.rules)
    for rule in ap.rules:
        assert isinstance(rule.severity_level, SeverityLevel)
        assert isinstance(rule.tag_filter, AlertingProfileTagFilter)
        assert isinstance(rule.tag_filter.include_mode, TagFilterIncludeMode)
        assert isinstance(rule.tag_filter.tag_filters, list)
        for tf in rule.tag_filter.tag_filters:
            assert isinstance(tf, METag)
        assert isinstance(rule.delay_in_minutes, int)
    assert isinstance(ap.management_zone_id, str)
    assert isinstance(ap.event_type_filters, list)
    first_event = ap.event_type_filters[0]
    assert isinstance(first_event, AlertingEventTypeFilter)
    assert isinstance(first_event.custom_event_filter, AlertingCustomEventFilter)
    assert isinstance(
        first_event.custom_event_filter.custom_title_filter, AlertingCustomTextFilter
    )
    assert isinstance(first_event.custom_event_filter.custom_title_filter.enabled, bool)
    assert isinstance(first_event.custom_event_filter.custom_title_filter.value, str)
    assert isinstance(
        first_event.custom_event_filter.custom_title_filter.operator,
        StringComparisonOperator,
    )
    assert isinstance(first_event.custom_event_filter.custom_title_filter.negate, bool)
    assert isinstance(
        first_event.custom_event_filter.custom_title_filter.case_insensitive, bool
    )
    second_event = ap.event_type_filters[1]
    assert isinstance(second_event, AlertingEventTypeFilter)
    assert isinstance(
        second_event.predefined_event_filter, AlertingPredefinedEventFilter
    )
    assert isinstance(
        second_event.predefined_event_filter.event_type, AlertingPredefinedEvent
    )
    assert isinstance(second_event.predefined_event_filter.negate, bool)

    # value checks
    assert ap.id == ID
    assert ap.display_name == NAME
    rule = ap.rules[0]
    assert rule.severity_level == SeverityLevel.PERFORMANCE
    assert rule.tag_filter.include_mode == TagFilterIncludeMode.INCLUDE_ANY
    assert rule.delay_in_minutes == 25
    assert ap.management_zone_id == "-6238974133282121422"
    custom_event_filter = ap.event_type_filters[
        0
    ].custom_event_filter.custom_title_filter
    predef_event_filter = ap.event_type_filters[1].predefined_event_filter
    assert custom_event_filter.enabled
    assert custom_event_filter.value == "ERROR"
    assert custom_event_filter.operator == StringComparisonOperator.CONTAINS
    assert not custom_event_filter.negate
    assert not custom_event_filter.case_insensitive
    assert predef_event_filter.event_type == AlertingPredefinedEvent.OSI_HIGH_CPU
    assert not predef_event_filter.negate


async def test_post(dt: DynatraceAsync):
    response = await dt.alerting_profiles.post(
        AlertingProfile(
            raw_element={
                "id": ID,
                "displayName": NAME,
                "description": "new_management_zone",
                "rules": [
                    {
                        "severityLevel": "PERFORMANCE",
                        "tagFilter": {
                            "includeMode": "INCLUDE_ANY",
                            "tagFilters": [
                                {
                                    "context": "CONTEXTLESS",
                                    "key": "Application",
                                    "value": "Custom",
                                }
                            ],
                        },
                        "delayInMinutes": 25,
                    }
                ],
            }
        )
    )

    # type checks
    assert isinstance(response, EntityShortRepresentation)
    # value checks
    assert response.id == ID
    assert response.name == NAME
