from datetime import datetime, timezone
from typing import Any

import pytest

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
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList
from test.async_utils import MockResponse, collect


async def test_list(dt: DynatraceAsync) -> None:
    extensions = await dt.extensions.list()
    assert isinstance(extensions, PaginatedList)

    extensions_list = await collect(extensions)
    assert len(extensions_list) == 35
    first = extensions_list[0]

    assert isinstance(first, ExtensionDto)
    assert first.id == "custom.remote.python.certificates"
    assert first.name == "Certificates Plugin"
    assert first.type == ExtensionType.ACTIVEGATE


async def test_get(dt: DynatraceAsync) -> None:
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


async def test_get_global_configuration(dt: DynatraceAsync) -> None:
    global_config = await dt.extensions.get_global_configuration(
        "custom.python.citrixAgent"
    )
    assert isinstance(global_config, GlobalExtensionConfiguration)
    assert global_config.extension_id == "custom.python.citrixAgent"
    assert global_config.enabled
    assert not global_config.infraOnlyEnabled
    assert global_config.properties is not None
    assert global_config.properties["log_level"] == "INFO"


async def test_get_state(dt: DynatraceAsync) -> None:
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
    assert first.timestamp == datetime.fromtimestamp(1620943873929 / 1000, timezone.utc)
    assert first.host_id is None
    assert first.process_id is None


async def test_get_instance_configuration(dt: DynatraceAsync) -> None:
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


async def test_put_instance_configuration(
    dt: DynatraceAsync, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[dict[str, Any]] = []

    async def fake_make_request(
        self: HttpClient,
        path: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        method: str = "GET",
        data: Any = None,
        query_params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> MockResponse:
        calls.append({"path": path, "params": params, "method": method})
        return MockResponse(None)

    monkeypatch.setattr(HttpClient, "make_request", fake_make_request)

    config = dt.extensions.create_instance(
        extension_id="custom.remote.python.demo",
        properties={"serverIp": "127.0.0.1"},
        enabled=True,
        use_global=False,
        activegate=EntityShortRepresentation(
            raw_element={"id": "7835970235169136995", "name": "ActiveGate Host Name"}
        ),
        endpoint_id="endpoint-id",
        endpoint_name="endpoint-name",
    )

    await dt.extensions.put_instance("configuration-id", config)

    assert calls == [
        {
            "path": "/api/config/v1/extensions/custom.remote.python.demo/instances/configuration-id",
            "params": {
                "extensionId": "custom.remote.python.demo",
                "enabled": True,
                "useGlobal": False,
                "properties": {"serverIp": "127.0.0.1"},
                "hostId": None,
                "activeGate": {
                    "id": "7835970235169136995",
                    "name": "ActiveGate Host Name",
                    "description": None,
                },
                "endpointId": "endpoint-id",
                "endpointName": "endpoint-name",
            },
            "method": "PUT",
        }
    ]


async def test_put_global_configuration(
    dt: DynatraceAsync, monkeypatch: pytest.MonkeyPatch
) -> None:
    calls: list[dict[str, Any]] = []

    async def fake_make_request(
        self: HttpClient,
        path: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        method: str = "GET",
        data: Any = None,
        query_params: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> MockResponse:
        calls.append({"path": path, "params": params, "method": method})
        return MockResponse(None)

    monkeypatch.setattr(HttpClient, "make_request", fake_make_request)

    config = GlobalExtensionConfiguration(
        raw_element={
            "enabled": True,
            "extensionId": "custom.remote.python.demo",
            "infraOnlyEnabled": False,
            "properties": {"serverIp": "127.0.0.1"},
        },
    )

    await dt.extensions.put_global_configuration(config)

    assert calls == [
        {
            "path": "/api/config/v1/extensions/custom.remote.python.demo/global",
            "params": {
                "enabled": True,
                "extensionId": "custom.remote.python.demo",
                "infraOnlyEnabled": False,
                "properties": {"serverIp": "127.0.0.1"},
            },
            "method": "PUT",
        }
    ]


async def test_list_activegate_extension_modules(dt: DynatraceAsync) -> None:
    modules = await dt.extensions.list_activegate_extension_modules()
    assert isinstance(modules, PaginatedList)

    list_modules = await collect(modules)
    assert isinstance(list_modules, list)

    first = list_modules[0]
    assert isinstance(first, EntityShortRepresentation)
    assert first.id == "-7885258652650793909"
    assert first.name == "arch-david"
