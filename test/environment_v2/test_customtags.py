from dynatrace import DynatraceAsync
from dynatrace.environment_v2.custom_tags import AddEntityTags, METag
from dynatrace.pagination import PaginatedList
from test.async_utils import collect

ENTITY_SELECTOR = "bilalhosts"


async def test_list(dt: DynatraceAsync):
    _tags = await dt.custom_tags.list(entity_selector=ENTITY_SELECTOR)

    # type checks
    assert isinstance(_tags, PaginatedList)
    tags = await collect(_tags)
    assert len(tags) == 2
    assert all(isinstance(n, METag) for n in tags)

    # value checks
    for t in tags:
        assert t.key == "mainApp"
        assert t.string_representation == "mainApp"
        assert str(t.context) == "CONTEXTLESS"
        break


async def test_post_no_value(dt: DynatraceAsync):
    tags = await dt.custom_tags.post(
        "entityId(CUSTOM_DEVICE-3B7788FE910B0F42)", [AddEntityTags("test-tag-no-value")]
    )
    for tag in tags.applied_tags:
        assert str(tag.context) == "CONTEXTLESS"
        assert tag.key == "test-tag-no-value"
        assert tag.value is None
        assert tag.string_representation == "test-tag-no-value"


async def test_post_value(dt: DynatraceAsync):
    tags = await dt.custom_tags.post(
        "entityId(CUSTOM_DEVICE-3B7788FE910B0F42)",
        [AddEntityTags("test-tag-value", "tag-value")],
    )
    for tag in tags.applied_tags:
        assert str(tag.context) == "CONTEXTLESS"
        assert tag.key == "test-tag-value"
        assert tag.value == "tag-value"
        assert tag.string_representation == "test-tag-value:tag-value"


async def test_delete(dt: DynatraceAsync):
    deleted_tags = await dt.custom_tags.delete(
        "test-tag-value",
        "entityId(CUSTOM_DEVICE-3B7788FE910B0F42)",
        delete_all_with_key=True,
    )
    assert deleted_tags.matched_entities_count == 1
