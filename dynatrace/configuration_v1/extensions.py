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

from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from httpx import Response

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.environment_v2.monitored_entities import EntityShortRepresentation
from dynatrace.environment_v2.schemas import ConfigurationMetadata
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList
from dynatrace.utils import (
    raw_optional_bool,
    raw_optional_dict,
    raw_optional_enum_or_str,
    raw_optional_int,
    raw_optional_object,
    raw_optional_object_list,
    raw_optional_str,
    raw_optional_str_list_or_none,
    raw_required_bool,
)


class ExtensionService:
    def __init__(self, http_client: HttpClient):
        self.__http_client = http_client

    async def list(self, page_size: int = 200) -> PaginatedList["ExtensionDto"]:
        """
        List all uploaded extensions

        :param page_size: The number of results per result page. Must be between 1 and 500
            Default value : 200
        """
        params = {"pageSize": page_size}
        return await PaginatedList(
            ExtensionDto,
            self.__http_client,
            "/api/config/v1/extensions",
            params,
            list_item="extensions",
        ).initialize()

    async def get(self, extension_id: str) -> "Extension":
        response = (
            await self.__http_client.make_request(
                f"/api/config/v1/extensions/{extension_id}"
            )
        ).json()
        return Extension(raw_element=response)

    async def post(self, zip_file_path: str) -> EntityShortRepresentation:

        file = Path(zip_file_path)
        with open(file, "rb") as f:
            response = await self.__http_client.make_request(
                "/api/config/v1/extensions", method="POST", files={"file": f}
            )

        return EntityShortRepresentation(raw_element=response.json())

    async def validate(self, zip_file_path: str) -> Response:

        file = Path(zip_file_path)
        with open(file, "rb") as f:
            return await self.__http_client.make_request(
                "/api/config/v1/extensions/validator", method="POST", files={"file": f}
            )

    async def list_instances(
        self, extension_id: str, page_size: int = 200
    ) -> PaginatedList["ExtensionShortRepresentation"]:
        params = {"pageSize": page_size}
        return await PaginatedList(
            ExtensionShortRepresentation,
            self.__http_client,
            f"/api/config/v1/extensions/{extension_id}/instances",
            list_item="configurationsList",
            target_params=params,
        ).initialize()

    async def get_instance(
        self, extension_id: str, configuration_id: str
    ) -> "ExtensionConfigurationDto":
        response = (
            await self.__http_client.make_request(
                f"/api/config/v1/extensions/{extension_id}/instances/{configuration_id}"
            )
        ).json()
        return ExtensionConfigurationDto(
            http_client=self.__http_client, raw_element=response
        )

    async def post_instance(
        self, extension_configuration: "ExtensionConfigurationDto"
    ) -> Response:
        return await extension_configuration.post()

    async def validate_instance(
        self, extension_configuration: "ExtensionConfigurationDto"
    ) -> Response:
        return await extension_configuration.validate()

    async def put_instance(
        self,
        configuration_id: str,
        extension_configuration: "ExtensionConfigurationDto",
    ) -> Response:
        return await extension_configuration.put(configuration_id)

    async def get_instance_configuration(
        self, extension_id: str, configuration_id: str
    ) -> "ExtensionConfigurationDto":
        response = (
            await self.__http_client.make_request(
                f"/api/config/v1/extensions/{extension_id}/instances/{configuration_id}"
            )
        ).json()
        return ExtensionConfigurationDto(
            http_client=self.__http_client, raw_element=response
        )

    async def delete_instance_configuration(
        self, extension_id: str, configuration_id: str
    ) -> Response:
        return await self.__http_client.make_request(
            f"/api/config/v1/extensions/{extension_id}/instances/{configuration_id}",
            method="DELETE",
        )

    async def get_global_configuration(
        self, extension_id: str
    ) -> "GlobalExtensionConfiguration":
        response = (
            await self.__http_client.make_request(
                f"/api/config/v1/extensions/{extension_id}/global"
            )
        ).json()
        return GlobalExtensionConfiguration(
            http_client=self.__http_client, raw_element=response
        )

    async def put_global_configuration(
        self, global_configuration: "GlobalExtensionConfiguration"
    ) -> Response:
        return await self.__http_client.make_request(
            f"/api/config/v1/extensions/{global_configuration.extension_id}/global",
            params=global_configuration.to_json(),
            method="PUT",
        )

    async def get_binary(self, extension_id: str) -> bytes:
        return (
            await self.__http_client.make_request(
                f"/api/config/v1/extensions/{extension_id}/binary"
            )
        ).content

    async def list_states(self, extension_id: str) -> PaginatedList["ExtensionState"]:
        return await PaginatedList(
            ExtensionState,
            self.__http_client,
            f"/api/config/v1/extensions/{extension_id}/states",
            list_item="states",
        ).initialize()

    async def list_activegate_extension_modules(
        self,
    ) -> PaginatedList[EntityShortRepresentation]:
        return await PaginatedList(
            EntityShortRepresentation,
            self.__http_client,
            "/api/config/v1/extensions/activeGateExtensionModules",
            list_item="values",
        ).initialize()

    def create_instance(
        self,
        extension_id: str,
        properties: dict[str, Any] | None = None,
        enabled: bool = True,
        use_global: bool = True,
        host_id: str | None = None,
        activegate: EntityShortRepresentation | None = None,
        endpoint_id: str | None = None,
        endpoint_name: str | None = None,
    ) -> "ExtensionConfigurationDto":

        raw_element = {
            "extensionId": extension_id,
            "enabled": enabled,
            "useGlobal": use_global,
            "properties": properties,
            "hostId": host_id,
            "activeGate": activegate._raw_element if activegate else {},
            "endpointId": endpoint_id,
            "endpointName": endpoint_name,
        }

        return ExtensionConfigurationDto(
            http_client=self.__http_client, raw_element=raw_element
        )


class ExtensionProperty(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.key: str | None = raw_optional_str(raw_element, "key")
        self.type: str | None = raw_optional_str(raw_element, "type")
        self.default_value: str | None = raw_optional_str(raw_element, "defaultValue")
        self.dropdown_values: list[str] | None = raw_optional_str_list_or_none(
            raw_element, "dropdownValues"
        )


class ExtensionConfigurationDto(DynatraceObject):
    async def post(self) -> Response:

        return await self._make_request(
            f"/api/config/v1/extensions/{self.extension_id}/instances",
            params=self.to_json(),
            method="POST",
        )

    async def validate(self) -> Response:
        return await self._make_request(
            f"/api/config/v1/extensions/{self.extension_id}/instances/validator",
            params=self.to_json(),
            method="POST",
        )

    async def put(self, configuration_id: str) -> Response:
        return await self._make_request(
            f"/api/config/v1/extensions/{self.extension_id}/instances/{configuration_id}",
            params=self.to_json(),
            method="PUT",
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "extensionId": self.extension_id,
            "enabled": self.enabled,
            "useGlobal": self.use_global,
            "properties": self.properties,
            "hostId": self.host_id,
            "activeGate": self.active_gate.to_json() if self.active_gate else None,
            "endpointId": self.endpoint_id,
            "endpointName": self.endpoint_name,
        }

    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.extension_id: str | None = raw_optional_str(raw_element, "extensionId")
        self.enabled: bool = raw_required_bool(raw_element, "enabled")
        self.use_global: bool = raw_required_bool(raw_element, "useGlobal")
        self.properties: dict[str, Any] | None = raw_optional_dict(
            raw_element, "properties"
        )
        self.host_id: str | None = raw_optional_str(raw_element, "hostId")
        self.active_gate: EntityShortRepresentation | None = raw_optional_object(
            raw_element,
            "activeGate",
            lambda value: EntityShortRepresentation(self._http_client, None, value),
        )
        self.endpoint_id: str | None = raw_optional_str(raw_element, "endpointId")
        self.endpoint_name: str | None = raw_optional_str(raw_element, "endpointName")


class ExtensionShortRepresentation(EntityShortRepresentation):
    async def get_full_configuration(
        self, extension_id: str
    ) -> ExtensionConfigurationDto:
        """
        Gets the full extension configuration for this ExtensionShortRepresentation
        """
        response = (
            await self._make_request(
                f"/api/config/v1/extensions/{extension_id}/instances/{self.id}"
            )
        ).json()
        return ExtensionConfigurationDto(self._http_client, raw_element=response)


class Extension(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.id: str | None = raw_optional_str(raw_element, "id")
        self.name: str | None = raw_optional_str(raw_element, "name")
        self.type: ExtensionType | str | None = raw_optional_enum_or_str(
            ExtensionType, raw_element.get("type")
        )
        self.version: str | None = raw_optional_str(raw_element, "version")
        self.metric_group: str | None = raw_optional_str(raw_element, "metricGroup")
        self.metadata: ConfigurationMetadata | None = raw_optional_object(
            raw_element,
            "metadata",
            lambda value: ConfigurationMetadata(self._http_client, None, value),
        )
        self.properties: list[ExtensionProperty] | None = raw_optional_object_list(
            raw_element,
            "properties",
            lambda value: ExtensionProperty(self._http_client, None, value),
        )


class ExtensionType(Enum):
    ACTIVEGATE = "ACTIVEGATE"
    CODEMODULE = "CODEMODULE"
    JMX = "JMX"
    ONEAGENT = "ONEAGENT"
    PMI = "PMI"
    UNKNOWN = "UNKNOWN"


class ExtensionDto(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.id: str | None = raw_optional_str(raw_element, "id")
        self.name: str | None = raw_optional_str(raw_element, "name")
        self.type: ExtensionType | str | None = raw_optional_enum_or_str(
            ExtensionType, raw_element.get("type")
        )

    async def get_full_extension(self) -> Extension:
        """
        Gets the full extension for this ExtensionDto
        """
        response = (
            await self._make_request(f"/api/config/v1/extensions/{self.id}")
        ).json()
        return Extension(self._http_client, None, response)

    @property
    def instances(
        self, page_size: int = 200
    ) -> PaginatedList["ExtensionShortRepresentation"]:
        """
        Returns the list of instances for this extension
        :param page_size: Page size, default 200
        """
        params = {"pageSize": page_size}
        return PaginatedList(
            ExtensionShortRepresentation,
            self._http_client,
            f"/api/config/v1/extensions/{self.id}/instances",
            list_item="configurationsList",
            target_params=params,
        )

    async def delete(self) -> Response:
        """
        Deletes the ZIP file of this extension
        """
        return await self._make_request(
            f"/api/config/v1/extensions/{self.id}", method="DELETE"
        )


class GlobalExtensionConfiguration(DynatraceObject):
    async def put(self) -> Response:
        return await self._make_request(
            f"/api/config/v1/extensions/{self.extension_id}/global",
            params=self.to_json(),
            method="PUT",
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "extensionId": self.extension_id,
            "infraOnlyEnabled": self.infra_only_enabled,
            "properties": self.properties,
        }

    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.enabled: bool = raw_required_bool(raw_element, "enabled")
        self.extension_id: str | None = raw_optional_str(raw_element, "extensionId")
        self.infra_only_enabled: bool | None = raw_optional_bool(
            raw_element, "infraOnlyEnabled"
        )
        self.properties: dict[str, Any] | None = raw_optional_dict(
            raw_element, "properties"
        )


class ExtensionStateEnum(Enum):
    ERROR_AUTH = "ERROR_AUTH"
    ERROR_COMMUNICATION_FAILURE = "ERROR_COMMUNICATION_FAILURE"
    ERROR_CONFIG = "ERROR_CONFIG"
    ERROR_TIMEOUT = "ERROR_TIMEOUT"
    ERROR_UNKNOWN = "ERROR_UNKNOWN"
    INCOMPATIBLE = "INCOMPATIBLE"
    LIMIT_REACHED = "LIMIT_REACHED"
    NOTHING_TO_REPORT = "NOTHING_TO_REPORT"
    OK = "OK"
    STATE_TYPE_UNKNOWN = "STATE_TYPE_UNKNOWN"
    UNINITIALIZED = "UNINITIALIZED"
    UNSUPPORTED = "UNSUPPORTED"
    WAITING_FOR_STATE = "WAITING_FOR_STATE"


class ExtensionState(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.extension_id: str | None = raw_optional_str(raw_element, "extensionId")
        self.version: str | None = raw_optional_str(raw_element, "version")
        self.endpoint_id: str | None = raw_optional_str(raw_element, "endpointId")
        self.state: ExtensionStateEnum | str | None = raw_optional_enum_or_str(
            ExtensionStateEnum, raw_element.get("state")
        )
        self.state_description: str | None = raw_optional_str(
            raw_element, "stateDescription"
        )
        self.host_id: str | None = raw_optional_str(raw_element, "hostId")
        self.process_id: str | None = raw_optional_str(raw_element, "processId")
        timestamp = raw_optional_int(raw_element, "timestamp")
        self.timestamp: datetime | None = (
            datetime.fromtimestamp(timestamp / 1000, timezone.utc)
            if timestamp is not None
            else None
        )
