from datetime import UTC, datetime

from dynatrace import DynatraceAsync
from dynatrace.configuration_v1.extensions import (
    Extension,
    ExtensionConfigurationDto,
    ExtensionDto,
    ExtensionProperty,
    ExtensionState,
    ExtensionStateEnum,
    ExtensionType,
    GlobalExtensionConfiguration,
)
from dynatrace.environment_v2.monitored_entities import EntityShortRepresentation
from dynatrace.pagination import PaginatedList
from test.async_utils import collect


async def test_list(dt: DynatraceAsync):
    extensions = await dt.extensions.list()
    assert isinstance(extensions, PaginatedList)

    extensions_list = await collect(extensions)
    assert len(extensions_list) == 35
    first = extensions_list[0]

    assert isinstance(first, ExtensionDto)
    assert first.id == "custom.remote.python.certificates"
    assert first.name == "Certificates Plugin"
    assert first.type == ExtensionType.ACTIVEGATE


async def test_get(dt: DynatraceAsync):
    extension = await dt.extensions.get("custom.python.citrixAgent")
    assert isinstance(extension, Extension)
    assert extension.id == "custom.python.citrixAgent"
    assert extension.name == "Citrix Virtual Apps & Virtual Desktops"
    assert extension.version == "2.034"
    assert extension.type == ExtensionType.ONEAGENT
    assert extension.metric_group == "tech.Citrix"
    assert isinstance(extension.properties, list)

    first_property = extension.properties[0]
    assert isinstance(first_property, ExtensionProperty)
    assert first_property.key == "openkit_verify_certificates"
    assert first_property.type == "BOOLEAN"


async def test_get_global_configuration(dt: DynatraceAsync):
    global_config = await dt.extensions.get_global_configuration(
        "custom.python.citrixAgent"
    )
    assert isinstance(global_config, GlobalExtensionConfiguration)
    assert global_config.extension_id == "custom.python.citrixAgent"
    assert global_config.enabled
    assert not global_config.infraOnlyEnabled
    assert global_config.properties["log_level"] == "INFO"


async def test_get_state(dt: DynatraceAsync):
    states = await dt.extensions.list_states(
        "custom.remote.python.salesforce_eventstream"
    )
    assert isinstance(states, PaginatedList)

    list_states = await collect(states)
    assert isinstance(list_states, list)

    first = list_states[0]
    assert isinstance(first, ExtensionState)
    assert first.extension_id == "custom.remote.python.salesforce_eventstream"
    assert first.version == ""
    assert first.endpoint_id == "5649014104314746667"
    assert first.state == ExtensionStateEnum.ERROR_CONFIG
    assert first.state_description == "Extension doesn't exist on given host"
    assert first.timestamp == datetime.fromtimestamp(1620943873929 / 1000, UTC)
    assert first.host_id is None
    assert first.process_id is None


async def test_get_instance_configuration(dt: DynatraceAsync):
    config = await dt.extensions.get_instance_configuration(
        "custom.remote.python.salesforce_eventstream", "5649014104314746667"
    )
    assert isinstance(config, ExtensionConfigurationDto)

    # TODO - This is a bug on Dynatrace, watch for the fix, this is the configuration ID
    assert config.extension_id == "5649014104314746667"

    assert config.enabled
    assert config.active_gate.id == "-7885258652650793909"
    assert config.active_gate.name == "arch-david"
    assert config.endpoint_id == "5649014104314746667"
    assert config.endpoint_name == "curious-hawk"
    assert (
        config.properties["openkit_application_id"]
        == "87eee414-9338-446b-988b-bbdbf495c4f4"
    )


async def test_list_activegate_extension_modules(dt: DynatraceAsync):
    modules = await dt.extensions.list_activegate_extension_modules()
    assert isinstance(modules, PaginatedList)

    list_modules = await collect(modules)
    assert isinstance(list_modules, list)

    first = list_modules[0]
    assert isinstance(first, EntityShortRepresentation)
    assert first.id == "-7885258652650793909"
    assert first.name == "arch-david"
