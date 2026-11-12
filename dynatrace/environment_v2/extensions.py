"""
Copyright 2021 Dynatrace LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import builtins
from datetime import datetime
from pathlib import Path
from typing import Any, cast

from httpx import Response

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList
from dynatrace.utils import (
    raw_optional_int,
    raw_optional_str,
    raw_optional_str_list,
    raw_required_int,
    raw_required_str,
    timestamp_to_string,
)


class ExtensionsServiceV2:
    ENDPOINT = "/api/v2/extensions"
    SCHEMA_ENDPOINT = "/api/v2/extensions/schemas"

    def __init__(self, http_client: HttpClient):
        self.__http_client = http_client

    async def list(self, name: str | None = None) -> PaginatedList["MinimalExtension"]:
        """Lists all the extensions 2.0 available in your environment"""
        params = {"name": name}
        return await PaginatedList(
            MinimalExtension,
            self.__http_client,
            target_url=self.ENDPOINT,
            list_item="extensions",
            target_params=params,
        ).initialize()

    async def list_versions(
        self, extension_name: str
    ) -> PaginatedList["MinimalExtension"]:
        """Lists all the extensions 2.0 by specified name in your environment

        :param extension_name: the name of the extension 2.0
        """
        return await PaginatedList(
            MinimalExtension,
            self.__http_client,
            target_url=f"{self.ENDPOINT}/{extension_name}",
            list_item="extensions",
        ).initialize()

    async def list_infos(
        self, name: str | None = None
    ) -> PaginatedList["ExtensionInfo"]:
        """Lists installed extensions together with their active version and keywords."""
        return await PaginatedList(
            ExtensionInfo,
            self.__http_client,
            target_url=f"{self.ENDPOINT}/info",
            list_item="extensions",
            target_params={"name": name},
        ).initialize()

    async def install(
        self, extension_name: str, version: str | None = None
    ) -> "RegisteredExtensionResult":
        """Installs an extension from Dynatrace Hub."""
        response = (
            await self.__http_client.make_request(
                f"{self.ENDPOINT}/{extension_name}",
                method="POST",
                query_params={"version": version},
            )
        ).json()
        return RegisteredExtensionResult(raw_element=response)

    async def list_environment_config_events(
        self, extension_name: str
    ) -> PaginatedList["ExtensionEventDTO"]:
        """List of the latest extension environment configuration events

        :param extension_name: the name of the extension 2.0

        :return: a list of ExtensionEventDTO object
        """
        return await PaginatedList(
            ExtensionEventDTO,
            self.__http_client,
            target_url=f"{self.ENDPOINT}/{extension_name}/environmentConfiguration/events",
            list_item="extensionEvents",
        ).initialize()

    async def list_monitoring_config_events(
        self, extension_name: str, config_id: str
    ) -> PaginatedList["ExtensionEventDTO"]:
        """Gets the list of the events linked to specific monitoring configuration

        :param extension_name: the name of the extension 2.0
        :param config_id: The ID of the requested monitoring configuration.

        :return: a list of ExtensionEventDTO object
        """
        return await PaginatedList(
            ExtensionEventDTO,
            self.__http_client,
            target_url=f"{self.ENDPOINT}/{extension_name}/monitoringConfigurations/{config_id}/events",
            list_item="extensionEvents",
        ).initialize()

    async def get(self, extension_name: str, extension_version: str) -> "Extension":
        """Gets details of specified version of the extension 2.0

        :param extension_name: the name of the requested extension 2.0
        :param extension_version: the version of the requested extension 2.0

        :return: a Extension class object
        """
        response = (
            await self.__http_client.make_request(
                f"{self.ENDPOINT}/{extension_name}/{extension_version}"
            )
        ).json()
        return Extension(raw_element=response)

    async def post(
        self, zip_file_path: str | Path, validate_only: bool | None = False
    ) -> "ExtensionUploadResponse":
        """Post the specified version of the extension 2.0

        :param zip_file_path: path to zipped extension 2.0
        :param validate_only: optionally run validation but do not persist the extension even if validation was successful

        :return: newly created Extension class object
        """
        params = {"validateOnly": validate_only}
        file = Path(zip_file_path)
        with open(file, "rb") as f:
            response = (
                await self.__http_client.make_request(
                    f"{self.ENDPOINT}",
                    query_params=params,
                    headers={"Content-Type": "application/octet-stream"},
                    method="POST",
                    data=f,
                )
            ).json()
            return ExtensionUploadResponse(raw_element=response)

    async def delete(self, extension_name: str, extension_version: str) -> "Extension":
        """Deletes the specified version of the extension 2.0

        :param extension_name: the name of the requested extension 2.0
        :param extension_version: the version of the requested extension 2.0

        :return: deleted extension
        """
        response = await self.__http_client.make_request(
            f"{self.ENDPOINT}/{extension_name}/{extension_version}", method="DELETE"
        )
        return Extension(raw_element=response.json())

    async def get_content(
        self, extension_name: str, extension_version: str, accept: str
    ) -> bytes:
        """Downloads an extension definition in the requested representation."""
        return (
            await self.__http_client.make_request(
                f"{self.ENDPOINT}/{extension_name}/{extension_version}",
                headers={"Accept": accept},
            )
        ).content

    async def get_environment_config(
        self, extension_name: str
    ) -> "ExtensionEnvironmentConfigurationVersion":
        """Gets the active environment configuration version of the specified extension 2.0

        :param extension_name: the name of the requested extension 2.0

        :return: ExtensionEnvironmentConfigurationVersion object
        """
        response = (
            await self.__http_client.make_request(
                f"{self.ENDPOINT}/{extension_name}/environmentConfiguration"
            )
        ).json()
        return ExtensionEnvironmentConfigurationVersion(raw_element=response)

    async def put_environment_config(
        self, extension_name: str, extension_version: str
    ) -> "ExtensionEnvironmentConfigurationVersion":
        """Updates an existing active environment configuration version of the extension 2.0

        :param extension_name: the name of the requested extension 2.0
        :param extension_version: the version of the requested extension 2.0

        :return: updated configuration version
        """
        response = await self.__http_client.make_request(
            f"{self.ENDPOINT}/{extension_name}/environmentConfiguration",
            method="PUT",
            json={"version": extension_version},
        )
        return ExtensionEnvironmentConfigurationVersion(raw_element=response.json())

    async def post_environment_config(
        self, extension_name: str, extension_version: str
    ) -> "ExtensionEnvironmentConfigurationVersion":
        """Activates the environment configuration from an extension version."""
        response = await self.__http_client.make_request(
            f"{self.ENDPOINT}/{extension_name}/environmentConfiguration",
            method="POST",
            json={"version": extension_version},
        )
        return ExtensionEnvironmentConfigurationVersion(raw_element=response.json())

    async def delete_environment_config(
        self, extension_name: str
    ) -> "ExtensionEnvironmentConfigurationVersion":
        """Deactivates the environment configuration of the specified extension 2.0

        :param extension_name: the name of the requested extension 2.0 to deactivate

        :return: deactivated configuration version
        """
        response = await self.__http_client.make_request(
            f"{self.ENDPOINT}/{extension_name}/environmentConfiguration",
            method="DELETE",
        )
        return ExtensionEnvironmentConfigurationVersion(raw_element=response.json())

    async def get_environment_config_assets(
        self, extension_name: str
    ) -> "ExtensionAssets":
        """Gets metadata for assets in the active environment configuration."""
        response = (
            await self.__http_client.make_request(
                f"{self.ENDPOINT}/{extension_name}/environmentConfiguration/assets"
            )
        ).json()
        return ExtensionAssets(raw_element=response)

    async def get_alert_template(
        self, extension_name: str, asset_id: str
    ) -> "AlertTemplate":
        """Gets an alert-template asset from the active environment configuration."""
        response = (
            await self.__http_client.make_request(
                f"{self.ENDPOINT}/{extension_name}/environmentConfiguration/"
                f"assets/alertTemplates/{asset_id}"
            )
        ).json()
        return AlertTemplate(raw_element=response)

    async def list_schemas_versions(self) -> builtins.list[str]:
        response = (
            await self.__http_client.make_request(f"{self.SCHEMA_ENDPOINT}")
        ).json()
        return cast(builtins.list[str], response.get("versions", []))

    async def list_schemas(self, schema_version: str) -> "SchemaFiles":
        response = await self.__http_client.make_request(
            f"{self.SCHEMA_ENDPOINT}/{schema_version}"
        )
        return SchemaFiles(raw_element=response.json())

    async def get_schema_file(
        self, schema_version: str, file_name: str
    ) -> dict[str, Any]:
        response = (
            await self.__http_client.make_request(
                f"{self.SCHEMA_ENDPOINT}/{schema_version}/{file_name}"
            )
        ).json()
        return cast(dict[str, Any], response)

    async def list_jmx_processes(
        self, host_id: str | None = None
    ) -> builtins.list["JavaProcessContainerList"]:
        """Lists Java processes available for JMX metric discovery."""
        response = (
            await self.__http_client.make_request(
                f"{self.ENDPOINT}/discovery/jmx/processes", params={"hostId": host_id}
            )
        ).json()
        return [JavaProcessContainerList(raw_element=item) for item in response]

    async def get_jmx_process(
        self, process_id: str, host_id: str | None = None
    ) -> "JavaProcessDetails":
        """Gets JMX discovery details for a Java process."""
        response = (
            await self.__http_client.make_request(
                f"{self.ENDPOINT}/discovery/jmx/processes/{process_id}",
                params={"hostId": host_id},
            )
        ).json()
        return JavaProcessDetails(raw_element=response)

    async def list_pmi_processes(
        self, host_id: str | None = None
    ) -> builtins.list["JavaProcessContainerList"]:
        """Lists Java processes available for PMI metric discovery."""
        response = (
            await self.__http_client.make_request(
                f"{self.ENDPOINT}/discovery/pmi/processes", params={"hostId": host_id}
            )
        ).json()
        return [JavaProcessContainerList(raw_element=item) for item in response]

    async def get_pmi_process(
        self, process_id: str, host_id: str | None = None
    ) -> "PmiProcessDetails":
        """Gets PMI discovery details for a Java process."""
        response = (
            await self.__http_client.make_request(
                f"{self.ENDPOINT}/discovery/pmi/processes/{process_id}",
                params={"hostId": host_id},
            )
        ).json()
        return PmiProcessDetails(raw_element=response)

    async def post_monitoring_configurations(
        self,
        extension_name: str,
        configurations: builtins.list["MonitoringConfigurationDto"],
    ) -> builtins.list["MonitoringConfigurationResponse"]:
        payload = [configuration.to_json() for configuration in configurations]
        response = await self.__http_client.make_request(
            f"{self.ENDPOINT}/{extension_name}/monitoringConfigurations",
            json=payload,
            method="POST",
        )
        return [
            MonitoringConfigurationResponse(raw_element=item)
            for item in cast(builtins.list[dict[str, Any]], response.json())
        ]

    async def list_monitoring_configurations(
        self,
        extension_name: str,
        version: str | None = None,
        active: bool | None = None,
    ) -> PaginatedList["ExtensionMonitoringConfiguration"]:
        params = {"version": version, "active": active}
        return await PaginatedList(
            ExtensionMonitoringConfiguration,
            self.__http_client,
            target_url=f"{self.ENDPOINT}/{extension_name}/monitoringConfigurations",
            target_params=params,
            list_item="items",
        ).initialize()

    async def get_monitoring_configuration(
        self, extension_name: str, config_id: str
    ) -> "ExtensionMonitoringConfiguration":
        """Gets a monitoring configuration by ID."""
        response = (
            await self.__http_client.make_request(
                f"{self.ENDPOINT}/{extension_name}/monitoringConfigurations/{config_id}"
            )
        ).json()
        return ExtensionMonitoringConfiguration(raw_element=response)

    async def put_monitoring_configuration(
        self, extension_name: str, config_id: str, value: dict[str, Any]
    ) -> "MonitoringConfigurationResponse":
        url = f"{self.ENDPOINT}/{extension_name}/monitoringConfigurations/{config_id}"
        response = await self.__http_client.make_request(
            url, method="PUT", json={"value": value}
        )
        return MonitoringConfigurationResponse(raw_element=response.json())

    async def delete_monitoring_configuration(
        self, extension_name: str, config_id: str
    ) -> Response:
        url = f"{self.ENDPOINT}/{extension_name}/monitoringConfigurations/{config_id}"
        return await self.__http_client.make_request(url, method="DELETE")

    async def list_monitoring_configuration_statuses(
        self, extension_name: str
    ) -> builtins.list["ExtensionStatusWithId"]:
        """Gets the latest status of every monitoring configuration of an extension."""
        response = (
            await self.__http_client.make_request(
                f"{self.ENDPOINT}/{extension_name}/monitoringConfigurations/status"
            )
        ).json()
        return [ExtensionStatusWithId(raw_element=item) for item in response]

    async def get_monitoring_configuration_status(
        self, extension_name: str, config_id: str
    ) -> "ExtensionStatus":
        """Gets the latest execution status of a monitoring configuration."""
        response = (
            await self.__http_client.make_request(
                f"{self.ENDPOINT}/{extension_name}/monitoringConfigurations/"
                f"{config_id}/status"
            )
        ).json()
        return ExtensionStatus(raw_element=response)

    async def execute_monitoring_configuration_actions(
        self, extension_name: str, config_id: str, actions: dict[str, Any]
    ) -> "ExecuteActionsResponse":
        """Executes data-source actions for a monitoring configuration."""
        response = await self.__http_client.make_request(
            f"{self.ENDPOINT}/{extension_name}/monitoringConfigurations/"
            f"{config_id}/actions",
            method="PUT",
            json={"actions": actions},
        )
        return ExecuteActionsResponse(raw_element=response.json())

    async def list_monitoring_configuration_audit_logs(
        self,
        extension_name: str,
        config_id: str,
        time_from: datetime | str | None = None,
        time_to: datetime | str | None = None,
        sort: str | None = None,
    ) -> PaginatedList["ExtensionMonitoringConfigurationAuditLogEntry"]:
        """Lists audit-log entries for a monitoring configuration."""
        return await PaginatedList(
            ExtensionMonitoringConfigurationAuditLogEntry,
            self.__http_client,
            target_url=f"{self.ENDPOINT}/{extension_name}/monitoringConfigurations/"
            f"{config_id}/audit",
            target_params={
                "from": timestamp_to_string(time_from),
                "to": timestamp_to_string(time_to),
                "sort": sort,
            },
            list_item="auditLogs",
        ).initialize()

    async def get_active_gate_groups(
        self, extension_name: str, extension_version: str
    ) -> "ActiveGateGroupsInfo":
        """Lists ActiveGate groups available for an extension version."""
        response = (
            await self.__http_client.make_request(
                f"{self.ENDPOINT}/{extension_name}/{extension_version}/activeGateGroups"
            )
        ).json()
        return ActiveGateGroupsInfo(raw_element=response)

    async def get_configuration_schema(
        self, extension_name: str, extension_version: str
    ) -> dict[str, Any]:
        """Gets the configuration schema of an extension version."""
        response = (
            await self.__http_client.make_request(
                f"{self.ENDPOINT}/{extension_name}/{extension_version}/schema"
            )
        ).json()
        return cast(dict[str, Any], response)


class SchemaFiles(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.files: list[str] = raw_element.get("files", [])


class RegisteredExtensionResult(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.extension_name: str | None = raw_optional_str(raw_element, "extensionName")
        self.extension_version: str | None = raw_optional_str(
            raw_element, "extensionVersion"
        )


class ExtensionInfo(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.extension_name: str = raw_required_str(raw_element, "extensionName")
        self.version: str = raw_required_str(raw_element, "version")
        self.active_version: str | None = raw_optional_str(raw_element, "activeVersion")
        self.keywords: list[str] = raw_optional_str_list(raw_element, "keywords")


class ExtensionAssets(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.assets: builtins.list[AssetInfo] = [
            AssetInfo(raw_element=asset)
            for asset in cast(builtins.list[dict[str, Any]], raw_element["assets"])
        ]
        self.errors: list[str] = raw_optional_str_list(raw_element, "errors")
        self.status: str = raw_required_str(raw_element, "status")
        self.version: str = raw_required_str(raw_element, "version")


class AlertTemplate(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.template_json: str | None = raw_optional_str(raw_element, "templateJson")


class AssetInfo(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.asset_schema_details: dict[str, Any] | None = cast(
            dict[str, Any] | None, raw_element.get("assetSchemaDetails")
        )
        self.display_name: str | None = raw_optional_str(raw_element, "displayName")
        self.id: str | None = raw_optional_str(raw_element, "id")
        self.type: str | None = raw_optional_str(raw_element, "type")


class JavaProcessContainerList(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.items: builtins.list[JavaProcessContainer] = [
            JavaProcessContainer(raw_element=item)
            for item in cast(builtins.list[dict[str, Any]], raw_element["items"])
        ]


class JavaProcessContainer(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.agent_version: str | None = raw_optional_str(raw_element, "agentVersion")
        self.id: str | None = raw_optional_str(raw_element, "id")
        self.name: str | None = raw_optional_str(raw_element, "name")
        self.properties: dict[str, builtins.list[str]] | None = cast(
            dict[str, builtins.list[str]] | None, raw_element.get("properties")
        )


class JavaProcessDetails(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.details: dict[str, Any] = raw_element


class PmiProcessDetails(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.details: dict[str, Any] = raw_element


class Extension(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.version: str = raw_required_str(raw_element, "version")
        self.extension_name: str = raw_required_str(raw_element, "extensionName")
        self.min_dynatrace_version: str = raw_required_str(
            raw_element, "minDynatraceVersion"
        )
        self.min_eec_version: str | None = raw_optional_str(
            raw_element, "minEECVersion"
        )
        self.file_hash: str = raw_required_str(raw_element, "fileHash")
        self.author: AuthorDTO = AuthorDTO(raw_element=raw_element["author"])
        self.data_sources: list[str] = raw_optional_str_list(raw_element, "dataSources")
        self.variables: list[str] = raw_optional_str_list(raw_element, "variables")
        self.feature_sets: list[str] = raw_optional_str_list(raw_element, "featureSets")
        self.assets_info: list[dict[str, Any]] = cast(
            list[dict[str, Any]], raw_element.get("assetsInfo", [])
        )
        self.feature_sets_details: dict[str, Any] = cast(
            dict[str, Any], raw_element.get("featureSetsDetails", {})
        )


class ExtensionUploadResponse(Extension):
    """Response returned after uploading or validating an extension archive."""


class AuthorDTO(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.name: str | None = raw_element.get("name")


class ExtensionEventDTO(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.timestamp: str | None = raw_element.get("timestamp")
        self.severity: str | None = raw_element.get("severity")
        self.message: str | None = raw_element.get("message")


class ExtensionEnvironmentConfigurationVersion(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.version: str = raw_required_str(raw_element, "version")

    def to_json(self) -> dict[str, Any]:
        """Translates an ExtensionEnvironmentConfigurationVersion to a JSON dict."""
        return {"version": self.version}

    async def put(
        self, extension_name: str
    ) -> "ExtensionEnvironmentConfigurationVersion":
        """Updates an existing extension environment config's version in Dynatrace

        :param extension_name: the name of the extension required for making the API call
        """
        response = await self._make_request(
            f"{ExtensionsServiceV2.ENDPOINT}/{extension_name}/environmentConfiguration",
            params=self.to_json(),
            method="PUT",
        )
        return ExtensionEnvironmentConfigurationVersion(raw_element=response.json())


class MinimalExtension(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.version: str = raw_required_str(raw_element, "version")
        self.extension_name: str = raw_required_str(raw_element, "extensionName")

    def list_version(self) -> str:
        """Class method for obtaining extension2.0 version"""
        return self.version

    async def get_environment_config(
        self,
    ) -> "ExtensionEnvironmentConfigurationVersion":
        """Gets the active environment configuration version of the specified extension 2.0

        :return: ExtensionEnvironmentConfigurationVersion object
        """
        response = (
            await self._make_request(
                f"{ExtensionsServiceV2.ENDPOINT}/{self.extension_name}/environmentConfiguration"
            )
        ).json()
        return ExtensionEnvironmentConfigurationVersion(raw_element=response)

    async def list_environment_config_events(
        self,
    ) -> PaginatedList["ExtensionEventDTO"]:
        """List of the latest extension environment configuration events

        :return: a list of ExtensionEventDTO object
        """
        return await PaginatedList(
            ExtensionEventDTO,
            self._http_client,
            target_url=f"{ExtensionsServiceV2.ENDPOINT}/{self.extension_name}/environmentConfiguration/events",
            list_item="extensionEvents",
        ).initialize()

    async def list_monitoring_config_events(
        self, config_id: str
    ) -> PaginatedList["ExtensionEventDTO"]:
        """Gets the list of the events linked to specific monitoring configuration

        :param config_id: The ID of the requested monitoring configuration.

        :return: a list of ExtensionEventDTO object
        """
        return await PaginatedList(
            ExtensionEventDTO,
            self._http_client,
            target_url=f"{ExtensionsServiceV2.ENDPOINT}/{self.extension_name}/monitoringConfigurations/{config_id}/events",
            list_item="extensionEvents",
        ).initialize()


class MonitoringConfigurationDto:
    def __init__(self, scope: str, configuration: dict[str, Any]):
        self.scope = scope
        self.configuration = configuration

    def to_json(self) -> dict[str, Any]:
        return {"scope": self.scope, "value": self.configuration}


class ExtensionMonitoringConfiguration(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.objectId: str = raw_required_str(raw_element, "objectId")
        self.scope: str = raw_required_str(raw_element, "scope")
        self.configuration: dict[str, Any] = raw_element["value"]


class MonitoringConfigurationResponse(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.objectId: str = raw_required_str(raw_element, "objectId")
        self.code: int = raw_required_int(raw_element, "code")


class ExtensionStatus(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.status: str = raw_required_str(raw_element, "status")
        self.timestamp: int | None = raw_optional_int(raw_element, "timestamp")


class ExtensionStatusWithId(ExtensionStatus):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        super()._create_from_raw_data(raw_element)
        self.configuration_id: str = raw_required_str(raw_element, "configurationId")


class ExecuteActionsResponse(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.ag_id: str | None = raw_optional_str(raw_element, "agId")
        self.ag_ids: list[str] = raw_optional_str_list(raw_element, "agIds")
        self.ag_name: str | None = raw_optional_str(raw_element, "agName")


class ActiveGateGroupsInfo(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.active_gate_groups: builtins.list[ActiveGateGroupInfo] = [
            ActiveGateGroupInfo(raw_element=group)
            for group in cast(
                builtins.list[dict[str, Any]], raw_element["activeGateGroups"]
            )
        ]


class ActiveGateGroupInfo(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.active_gates: builtins.list[ActiveGateInfo] = [
            ActiveGateInfo(raw_element=active_gate)
            for active_gate in cast(
                builtins.list[dict[str, Any]], raw_element["activeGates"]
            )
        ]
        self.available_active_gates: int = raw_required_int(
            raw_element, "availableActiveGates"
        )
        self.group_name: str = raw_required_str(raw_element, "groupName")


class ActiveGateInfo(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.errors: builtins.list[str] = raw_optional_str_list(raw_element, "errors")
        self.id: int = raw_required_int(raw_element, "id")


class ExtensionMonitoringConfigurationAuditLogEntry(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.raw: dict[str, Any] = raw_element
