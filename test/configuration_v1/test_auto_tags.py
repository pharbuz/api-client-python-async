from dynatrace import DynatraceAsync
from dynatrace.configuration_v1.auto_tags import (
    AutoTag,
    AutoTagRule,
    AutoTagShortRepresentation,
    ComparisonBasic,
    ComparisonBasicType,
    ConditionKey,
    ConditionKeyAttribute,
    EntityRuleEngineCondition,
    RuleType,
)
from dynatrace.environment_v2.schemas import ConfigurationMetadata
from dynatrace.pagination import PaginatedList


async def test_list(dt: DynatraceAsync):
    tags = await dt.auto_tags.list()
    assert isinstance(tags, PaginatedList)

    async for tag in tags:
        assert isinstance(tag, AutoTagShortRepresentation)
        assert tag.id == "403e033b-7324-4bfe-bef1-b3f367de42f2"
        assert tag.name == "frontend"
        break


async def test_get(dt: DynatraceAsync):
    tags = await dt.auto_tags.list()
    async for tag in tags:
        full_tag = await tag.get_full_configuration()
        assert isinstance(full_tag, AutoTag)
        assert isinstance(full_tag.metadata, ConfigurationMetadata)
        assert full_tag.metadata.cluster_version == "1.214.112.20210409-064503"
        assert full_tag.id == "403e033b-7324-4bfe-bef1-b3f367de42f2"
        assert full_tag.name == "frontend"
        assert isinstance(full_tag.rules, list)
        for rule in full_tag.rules:
            assert isinstance(rule, AutoTagRule)
            assert rule.type == RuleType.SERVICE
            assert rule.enabled
            assert rule.value_format == ""
            assert rule.propagation_types == []
            assert isinstance(rule.conditions, list)
            for condition in rule.conditions:
                assert isinstance(condition, EntityRuleEngineCondition)
                assert isinstance(condition.key, ConditionKey)
                assert (
                    condition.key.attribute == ConditionKeyAttribute.PROCESS_GROUP_NAME
                )
                assert isinstance(condition.comparison_info, ComparisonBasic)
                assert condition.comparison_info.type == ComparisonBasicType.STRING
                assert condition.comparison_info.operator == "CONTAINS"
                assert condition.comparison_info.value == "frontend"
                assert not condition.comparison_info.negate
                assert not condition.comparison_info.case_sensitive
                break
            break
        break
