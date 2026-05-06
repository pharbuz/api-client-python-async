from dynatrace import DynatraceAsync
from dynatrace.environment_v2.remote_configuration import (
    AttributeType,
    EntityType,
    OperationType,
    RemoteConfigurationManagementJobPreview,
    RemoteConfigurationManagementJobSummary,
    RemoteConfigurationManagementOperation,
)
from dynatrace.pagination import PaginatedList

TEST_ENTITY_ID = "0x2b7c0b02"


async def test_list(dt: DynatraceAsync):
    jobs = await dt.activegates_remote_configuration.list()

    assert isinstance(jobs, PaginatedList)

    async for job in jobs:
        assert isinstance(job, RemoteConfigurationManagementJobSummary)
        assert hasattr(job, "id")
        assert hasattr(job, "entity_type")
        assert hasattr(job, "start_time")
        assert isinstance(job.entity_type, EntityType)
        break


async def test_post(dt: DynatraceAsync):
    operation = RemoteConfigurationManagementOperation.build(
        attribute=AttributeType.NETWORK_ZONE,
        operation=OperationType.SET,
        value="test-zone",
    )

    job = await dt.activegates_remote_configuration.post(
        entities=[TEST_ENTITY_ID], operations=[operation]
    )

    assert job is not None
    assert job.id is not None
    assert job.entity_type == EntityType.ACTIVE_GATE
    assert len(job.operations) == 1
    assert job.operations[0].attribute == AttributeType.NETWORK_ZONE
    assert job.operations[0].operation == OperationType.SET
    assert job.operations[0].value == "test-zone"


async def test_get_current(dt: DynatraceAsync):
    current_job = await dt.activegates_remote_configuration.get_current()

    if current_job is not None:
        assert current_job.id is not None
        assert hasattr(current_job, "timeout_time")
        assert current_job.processed_entities_count <= current_job.total_entities_count


async def test_post_preview(dt: DynatraceAsync):
    operation = RemoteConfigurationManagementOperation.build(
        attribute=AttributeType.NETWORK_ZONE,
        operation=OperationType.SET,
        value="test-zone",
    )

    previews = await dt.activegates_remote_configuration.post_preview(
        entities=[TEST_ENTITY_ID],
        operations=[operation],
    )

    assert isinstance(previews, PaginatedList)

    async for preview in previews:
        assert isinstance(preview, RemoteConfigurationManagementJobPreview)
        assert preview.attribute == AttributeType.NETWORK_ZONE
        assert preview.operation == OperationType.SET
        assert preview.value == "test-zone"
        assert isinstance(preview.already_configured_entities_count, int)
        assert isinstance(preview.target_entities_count, int)
        break


async def test_validate(dt: DynatraceAsync):
    operation = RemoteConfigurationManagementOperation.build(
        attribute=AttributeType.NETWORK_ZONE,
        operation=OperationType.SET,
        value="test-zone",
    )
    validation_result = await dt.activegates_remote_configuration.validate(
        entities=[TEST_ENTITY_ID], operations=[operation]
    )

    # If validation succeeds, result should be None
    # If validation fails, result should contain error details
    if validation_result is not None:
        assert hasattr(validation_result, "invalid_entities")
        assert hasattr(validation_result, "invalid_operations")
        assert isinstance(validation_result.invalid_entities, list)
        assert isinstance(validation_result.invalid_operations, list)


async def test_get_job(dt: DynatraceAsync):
    ID = "7974003406714390819"
    job = await dt.activegates_remote_configuration.get(ID)

    assert job is not None
    assert job.id == ID
    assert job.entity_type == EntityType.ACTIVE_GATE
    assert len(job.operations) == 1
    assert job.operations[0].attribute == AttributeType.NETWORK_ZONE
    assert job.operations[0].operation == OperationType.SET
    assert job.operations[0].value == "test-zone"
