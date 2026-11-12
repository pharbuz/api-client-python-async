from typing import Any

import dynatrace.environment_v2.extensions as extensions_v2
from dynatrace import DynatraceAccessToken, DynatraceAsync
from dynatrace.environment_v2.extensions import (
    ExtensionsServiceV2,
    MinimalExtension,
    MonitoringConfigurationDto,
)
from dynatrace.http_client import HttpClient
from test.async_utils import MockResponse, collect


async def test_list(dt: DynatraceAsync) -> None:
    extensions = await collect(await dt.extensions_v2.list())

    assert len(extensions) == 2

    for extension in extensions:
        assert isinstance(extension, MinimalExtension)
        assert extension.extension_name == "com.dynatrace.extension.snmp-generic"
        assert extension.version == "0.2.5"
        break


async def test_list_name(dt: DynatraceAsync) -> None:
    extensions = await collect(await dt.extensions_v2.list(name="custom"))

    assert len(extensions) == 1

    for extension in extensions:
        assert isinstance(extension, MinimalExtension)
        assert extension.extension_name == "custom:dynatrace.cisco.asa"
        assert extension.version == "0.1.0"
        break


async def test_list_versions(dt: DynatraceAsync) -> None:
    extensions = await collect(
        await dt.extensions_v2.list_versions("com.dynatrace.extension.snmp-generic")
    )

    assert len(extensions) == 1

    for extension in extensions:
        assert isinstance(extension, MinimalExtension)
        assert extension.extension_name == "com.dynatrace.extension.snmp-generic"
        assert extension.version == "0.2.5"
        break


async def test_get(dt: DynatraceAsync) -> None:
    extension = await dt.extensions_v2.get(
        "com.dynatrace.extension.snmp-generic", "0.2.5"
    )

    # type checks
    assert isinstance(extension, extensions_v2.Extension)
    assert isinstance(extension.author, extensions_v2.AuthorDTO)
    assert isinstance(extension.data_sources, list)
    assert isinstance(extension.feature_sets, list)
    assert isinstance(extension.variables, list)

    # value checks
    assert extension.extension_name == "com.dynatrace.extension.snmp-generic"
    assert extension.author.name == "Dynatrace"
    assert extension.version == "0.2.5"
    assert extension.variables[0] == "ext.activationtag"


async def test_get_active_extension_version(dt: DynatraceAsync) -> None:
    environemnt_config = await dt.extensions_v2.get_environment_config("ibmmq")

    # type checks
    assert isinstance(
        environemnt_config, extensions_v2.ExtensionEnvironmentConfigurationVersion
    )

    # value checks
    assert environemnt_config.version == "1.2.3"


async def test_openapi_extension_endpoints_use_expected_requests(
    monkeypatch: Any, tmp_path: Any
) -> None:
    requests: list[tuple[str, str, dict[str, Any]]] = []
    extension = {
        "author": {"name": "Dynatrace"},
        "dataSources": [],
        "extensionName": "ext",
        "featureSets": [],
        "featureSetsDetails": {},
        "fileHash": "hash",
        "minDynatraceVersion": "1.0.0",
        "minEECVersion": "1.0.0",
        "variables": [],
        "version": "1.0.0",
    }

    async def make_request(
        self: HttpClient, path: str, method: str = "GET", **kwargs: Any
    ) -> MockResponse:
        requests.append((method, path, kwargs))
        if path == "/api/v2/extensions/info":
            return MockResponse(
                {
                    "extensions": [
                        {
                            "extensionName": "ext",
                            "version": "1.0.0",
                            "keywords": ["keyword"],
                        }
                    ],
                    "totalCount": 1,
                }
            )
        if path.endswith("/audit"):
            return MockResponse({"auditLogs": [{"logId": "1"}], "totalCount": 1})
        if path.endswith("/monitoringConfigurations") and method == "GET":
            return MockResponse({"items": [], "totalCount": 0})
        if path.endswith("/discovery/jmx/processes") or path.endswith(
            "/discovery/pmi/processes"
        ):
            return MockResponse([{"items": [{"id": "process"}]}])
        if "/discovery/" in path:
            return MockResponse({"attribute": "value"})
        if path.endswith("/assets"):
            return MockResponse(
                {
                    "assets": [{"id": "asset", "type": "ALERT_TEMPLATE"}],
                    "errors": [],
                    "status": "READY",
                    "version": "1.0.0",
                }
            )
        if "/alertTemplates/" in path:
            return MockResponse({"templateJson": "{}"})
        if path.endswith("/status"):
            if path.endswith("monitoringConfigurations/status"):
                return MockResponse(
                    [{"configurationId": "configuration", "status": "OK"}]
                )
            return MockResponse({"status": "OK"})
        if path.endswith("/actions"):
            return MockResponse({"agIds": ["ag"]})
        if path.endswith("/activeGateGroups"):
            return MockResponse(
                {
                    "activeGateGroups": [
                        {
                            "activeGates": [{"id": 1, "errors": []}],
                            "availableActiveGates": 1,
                            "groupName": "default",
                        }
                    ]
                }
            )
        if path.endswith("/schema"):
            return MockResponse({"schemaId": "schema"})
        if path.endswith("/environmentConfiguration"):
            return MockResponse({"version": "1.0.0"})
        if path.endswith("/monitoringConfigurations/configuration"):
            if method == "GET":
                return MockResponse(
                    {"objectId": "configuration", "scope": "environment", "value": {}}
                )
            if method == "PUT":
                return MockResponse({"objectId": "configuration", "code": 200})
            return MockResponse(None)
        if path.endswith("/monitoringConfigurations"):
            return MockResponse([{"objectId": "configuration", "code": 200}])
        if path == "/api/v2/extensions/ext" and method == "POST":
            return MockResponse({"extensionName": "ext", "extensionVersion": "1.0.0"})
        return MockResponse(extension)

    monkeypatch.setattr(HttpClient, "make_request", make_request)
    service = ExtensionsServiceV2(
        HttpClient("https://tenant", credentials=DynatraceAccessToken(token="token"))
    )

    await service.install("ext", "1.0.0")
    infos = await collect(await service.list_infos())
    assert infos[0].keywords == ["keyword"]
    archive = tmp_path / "extension.zip"
    archive.write_bytes(b"zip")
    await service.post(archive, validate_only=True)
    await service.delete("ext", "1.0.0")
    await service.get_content("ext", "1.0.0", "application/octet-stream")
    await service.post_environment_config("ext", "1.0.0")
    await service.put_environment_config("ext", "1.0.0")
    await service.delete_environment_config("ext")
    assets = await service.get_environment_config_assets("ext")
    assert assets.assets[0].id == "asset"
    await service.get_alert_template("ext", "asset")
    assert (await service.list_jmx_processes())[0].items[0].id == "process"
    await service.get_jmx_process("process")
    assert (await service.list_pmi_processes())[0].items[0].id == "process"
    await service.get_pmi_process("process")
    await service.post_monitoring_configurations(
        "ext", [MonitoringConfigurationDto("environment", {})]
    )
    await collect(await service.list_monitoring_configurations("ext"))
    await service.get_monitoring_configuration("ext", "configuration")
    await service.put_monitoring_configuration("ext", "configuration", {})
    await service.delete_monitoring_configuration("ext", "configuration")
    assert (await service.list_monitoring_configuration_statuses("ext"))[
        0
    ].status == "OK"
    await service.get_monitoring_configuration_status("ext", "configuration")
    await service.execute_monitoring_configuration_actions("ext", "configuration", {})
    await collect(
        await service.list_monitoring_configuration_audit_logs("ext", "configuration")
    )
    assert (await service.get_active_gate_groups("ext", "1.0.0")).active_gate_groups[
        0
    ].group_name == "default"
    assert (await service.get_configuration_schema("ext", "1.0.0"))[
        "schemaId"
    ] == "schema"

    assert (
        "POST",
        "/api/v2/extensions/ext",
        {"query_params": {"version": "1.0.0"}},
    ) in requests
    assert (
        "PUT",
        "/api/v2/extensions/ext/environmentConfiguration",
        {"json": {"version": "1.0.0"}},
    ) in requests
    assert (
        "POST",
        "/api/v2/extensions/ext/monitoringConfigurations",
        {"json": [{"scope": "environment", "value": {}}]},
    ) in requests
    assert (
        "PUT",
        "/api/v2/extensions/ext/monitoringConfigurations/configuration",
        {"json": {"value": {}}},
    ) in requests
