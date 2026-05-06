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
from pathlib import Path
from typing import Any

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList


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

    async def post(self, zip_file_path: str | Path, validate_only: bool | None = False):
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
                    files={"file": f},
                )
            ).json()
            return Extension(raw_element=response)

    async def delete(self, extension_name: str, extension_version: str):
        """Deletes the specified version of the extension 2.0

        :param extension_name: the name of the requested extension 2.0
        :param extension_version: the version of the requested extension 2.0

        :return: HTTP response
        """
        return await self.__http_client.make_request(
            f"{self.ENDPOINT}/{extension_name}/{extension_version}", method="DELETE"
        )

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

    async def put_environment_config(self, extension_name: str, extension_version: str):
        """Updates an existing active environment configuration version of the extension 2.0

        :param extension_name: the name of the requested extension 2.0
        :param extension_version: the version of the requested extension 2.0

        :return: HTTP response
        """
        params = {"version": extension_version}
        return await self.__http_client.make_request(
            f"{self.ENDPOINT}/{extension_name}/environmentConfiguration",
            method="PUT",
            params=params,
        )

    async def delete_environment_config(self, extension_name: str):
        """Deactivates the environment configuration of the specified extension 2.0

        :param extension_name: the name of the requested extension 2.0 to deactivate

        :return: HTTP response
        """
        return await self.__http_client.make_request(
            f"{self.ENDPOINT}/{extension_name}/environmentConfiguration",
            method="DELETE",
        )

    async def list_schemas_versions(self) -> builtins.list[str]:
        response = (
            await self.__http_client.make_request(f"{self.SCHEMA_ENDPOINT}")
        ).json()
        return response.get("versions", [])

    async def list_schemas(self, schema_version: str) -> "SchemaFiles":
        response = await self.__http_client.make_request(
            f"{self.SCHEMA_ENDPOINT}/{schema_version}"
        )
        return SchemaFiles(raw_element=response.json())

    async def get_schema_file(
        self, schema_version: str, file_name: str
    ) -> dict[str, Any]:
        return (
            await self.__http_client.make_request(
                f"{self.SCHEMA_ENDPOINT}/{schema_version}/{file_name}"
            )
        ).json()

    async def post_monitoring_configurations(
        self,
        extension_name: str,
        configurations: builtins.list["MonitoringConfigurationDto"],
    ) -> builtins.list:
        params = [c.to_json() for c in configurations]
        response = await self.__http_client.make_request(
            f"{self.ENDPOINT}/{extension_name}/monitoringConfigurations",
            params=params,
            method="POST",
        )
        return response.json()

    async def list_monitoring_configurations(
        self,
        extension_name: str,
        version: str | None = None,
        active: bool | None = None,
    ) -> PaginatedList["ExtensionMonitoringConfiguration"]:
        params = {"extensionName": extension_name, "version": version, "active": active}
        return await PaginatedList(
            ExtensionMonitoringConfiguration,
            self.__http_client,
            target_url=f"{self.ENDPOINT}/{extension_name}/monitoringConfigurations",
            target_params=params,
            list_item="items",
        ).initialize()

    async def put_monitoring_configuration(
        self, extension_name: str, config_id: str, value: dict[str, Any]
    ) -> "MonitoringConfigurationResponse":
        url = f"{self.ENDPOINT}/{extension_name}/monitoringConfigurations/{config_id}"
        params = {"value": value}
        response = await self.__http_client.make_request(
            url, method="PUT", params=params
        )
        return MonitoringConfigurationResponse(raw_element=response.json())

    async def delete_monitoring_configuration(
        self, extension_name: str, config_id: str
    ):
        url = f"{self.ENDPOINT}/{extension_name}/monitoringConfigurations/{config_id}"
        return await self.__http_client.make_request(url, method="DELETE")


class SchemaFiles(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.files: list[str] = raw_element.get("files", [])


class Extension(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.version: str = raw_element.get("version")
        self.extension_name: str = raw_element.get("extensionName")
        self.min_dynatrace_version: str = raw_element.get("minDynatraceVersion")
        self.file_hash: str = raw_element.get("fileHash")
        self.author: AuthorDTO = AuthorDTO(raw_element=raw_element.get("author"))
        self.data_sources: list[str] = raw_element.get("dataSources")
        self.variables: list[str] = raw_element.get("variables")
        self.feature_sets: list[str] = raw_element.get("featureSets")


class AuthorDTO(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.name: str = raw_element.get("name")


class ExtensionEventDTO(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.timestamp: str = raw_element.get("timestamp")
        self.severity: str = raw_element.get("severity")
        self.message: str = raw_element.get("message")


class ExtensionEnvironmentConfigurationVersion(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.version: str = raw_element.get("version")

    def to_json(self) -> dict[str, Any]:
        """Translates an ExtensionEnvironmentConfigurationVersion to a JSON dict."""
        return {"version": self.version}

    async def put(self, extension_name: str):
        """Updates an existing extension environment config's version in Dynatrace

        :param extension_name: the name of the extension required for making the API call
        """
        return await self._http_client.make_request(
            f"{ExtensionsServiceV2.ENDPOINT}/{extension_name}/environmentConfiguration",
            params=self.to_json(),
            method="PUT",
        )


class MinimalExtension(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.version: str = raw_element.get("version")
        self.extension_name: str = raw_element.get("extensionName")

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
            await self._http_client.make_request(
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
        self, config_id
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

    def to_json(self):
        return {"scope": self.scope, "value": self.configuration}


class ExtensionMonitoringConfiguration(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.objectId: str = raw_element.get("objectId")
        self.scope: str = raw_element.get("scope")
        self.configuration: dict[str, Any] = raw_element.get("value")


class MonitoringConfigurationResponse(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.objectId: str = raw_element.get("objectId")
        self.code: int = raw_element.get("code")
