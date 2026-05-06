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
from enum import Enum
from typing import Any, Optional

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList
from dynatrace.utils import timestamp_to_string


class ActiveGatesRemoteConfigurationService:
    ENDPOINT = "/api/v2/activeGates/remoteConfigurationManagement"

    def __init__(self, http_client: HttpClient) -> None:
        self.__http_client = http_client

    async def list(
        self,
        time_from: datetime | str | None = None,
        time_to: datetime | str | None = None,
    ) -> "PaginatedList[RemoteConfigurationManagementJobSummary]":
        """Lists finished ActiveGate remote configuration management jobs

        :param time_from: The start of the requested timeframe
        :param time_to: The end of the requested timeframe
        :return: A paginated list of remote configuration management job summaries
        """
        params = {
            "from": timestamp_to_string(time_from),
            "to": timestamp_to_string(time_to),
        }
        return await PaginatedList(
            RemoteConfigurationManagementJobSummary,
            self.__http_client,
            target_url=self.ENDPOINT,
            list_item="jobs",
            target_params=params,
        ).initialize()

    async def post(
        self,
        entities: builtins.list[str],
        operations: builtins.list["RemoteConfigurationManagementOperation"],
    ) -> "RemoteConfigurationManagementJob":
        """Creates a new remote configuration management job

        :param entities: The list of entities to apply the operations to
        :param operations: The list of operations to apply
        :return: The created job
        """
        payload = RemoteConfigurationManagementOperationActiveGateRequest(
            entities=entities, operations=operations
        )
        response = (
            await self.__http_client.make_request(
                self.ENDPOINT, method="POST", params=payload.to_json()
            )
        ).json()
        return RemoteConfigurationManagementJob(raw_element=response)

    async def get_current(self) -> Optional["RemoteConfigurationManagementJob"]:
        """Gets remote configuration management job that is currently running

        :return: The currently running job or None if no job is running
        """
        response = await self.__http_client.make_request(f"{self.ENDPOINT}/current")
        if not response.content:
            return None
        return RemoteConfigurationManagementJob(raw_element=response.json())

    async def post_preview(
        self,
        entities: builtins.list[str],
        operations: builtins.list["RemoteConfigurationManagementOperation"],
    ) -> "PaginatedList[RemoteConfigurationManagementJobPreview]":
        """Creates a preview for remote configuration management job

        :param entities: The list of entities to apply the operations to
        :param operations: The list of operations to apply
        :return: A paginated list of job previews
        """
        payload = RemoteConfigurationManagementOperationActiveGateRequest(
            entities=entities, operations=operations
        )
        return await PaginatedList(
            RemoteConfigurationManagementJobPreview,
            self.__http_client,
            target_url=f"{self.ENDPOINT}/preview",
            list_item="previews",
            target_params=payload.to_json(),
        ).initialize()

    async def validate(
        self,
        entities: builtins.list[str],
        operations: builtins.list["RemoteConfigurationManagementOperation"],
    ) -> Optional["RemoteConfigurationManagementValidationResult"]:
        """Validates the payload for a remote configuration management job

        :param entities: The list of entities to apply the operations to
        :param operations: The list of operations to apply
        :return: Validation result if validation failed, None if validation succeeded
        """
        payload = RemoteConfigurationManagementOperationActiveGateRequest(
            entities=entities, operations=operations
        )
        response = await self.__http_client.make_request(
            f"{self.ENDPOINT}/validator", method="POST", params=payload.to_json()
        )
        if not response.content:
            return None
        return RemoteConfigurationManagementValidationResult(
            raw_element=response.json()
        )

    async def get(self, job_id: str) -> "RemoteConfigurationManagementJob":
        """Gets the specified remote configuration management job

        :param job_id: The ID of the required job
        :return: The specified job
        """
        response = (
            await self.__http_client.make_request(f"{self.ENDPOINT}/{job_id}")
        ).json()
        return RemoteConfigurationManagementJob(raw_element=response)


class OneAgentsRemoteConfigurationService:
    ENDPOINT = "/api/v2/oneagents/remoteConfigurationManagement"

    def __init__(self, http_client: HttpClient) -> None:
        self.__http_client = http_client

    async def list(
        self,
        time_from: datetime | str | None = None,
        time_to: datetime | str | None = None,
    ) -> "PaginatedList[RemoteConfigurationManagementJobSummary]":
        """Lists finished OneAgent remote configuration management jobs

        :param time_from: The start of the requested timeframe
        :param time_to: The end of the requested timeframe
        :return: A paginated list of remote configuration management job summaries
        """
        params = {
            "from": timestamp_to_string(time_from),
            "to": timestamp_to_string(time_to),
        }
        return await PaginatedList(
            RemoteConfigurationManagementJobSummary,
            self.__http_client,
            target_url=self.ENDPOINT,
            list_item="jobs",
            target_params=params,
        ).initialize()

    async def post(
        self,
        entities: builtins.list[str],
        operations: builtins.list["RemoteConfigurationManagementOperation"],
    ) -> "RemoteConfigurationManagementJob":
        """Creates a new remote configuration management job

        :param entities: The list of entities to apply the operations to
        :param operations: The list of operations to apply
        :return: The created job
        """
        payload = RemoteConfigurationManagementOperationOneAgentRequest(
            entities=entities, operations=operations
        )
        response = (
            await self.__http_client.make_request(
                self.ENDPOINT, method="POST", params=payload.to_json()
            )
        ).json()
        return RemoteConfigurationManagementJob(raw_element=response)

    async def get_current(self) -> Optional["RemoteConfigurationManagementJob"]:
        """Gets remote configuration management job that is currently running

        :return: The currently running job or None if no job is running
        """
        response = await self.__http_client.make_request(f"{self.ENDPOINT}/current")
        if not response.content:
            return None
        return RemoteConfigurationManagementJob(raw_element=response.json())

    async def post_preview(
        self,
        entities: builtins.list[str],
        operations: builtins.list["RemoteConfigurationManagementOperation"],
    ) -> "PaginatedList[RemoteConfigurationManagementJobPreview]":
        """Creates a preview for remote configuration management job

        :param entities: The list of entities to apply the operations to
        :param operations: The list of operations to apply
        :return: A paginated list of job previews
        """
        payload = RemoteConfigurationManagementOperationOneAgentRequest(
            entities=entities, operations=operations
        )
        return await PaginatedList(
            RemoteConfigurationManagementJobPreview,
            self.__http_client,
            target_url=f"{self.ENDPOINT}/preview",
            list_item="previews",
            target_params=payload.to_json(),
        ).initialize()

    async def validate(
        self,
        entities: builtins.list[str],
        operations: builtins.list["RemoteConfigurationManagementOperation"],
    ) -> Optional["RemoteConfigurationManagementValidationResult"]:
        """Validates the payload for a remote configuration management job

        :param entities: The list of entities to apply the operations to
        :param operations: The list of operations to apply
        :return: Validation result if validation failed, None if validation succeeded
        """
        payload = RemoteConfigurationManagementOperationOneAgentRequest(
            entities=entities, operations=operations
        )
        response = await self.__http_client.make_request(
            f"{self.ENDPOINT}/validator", method="POST", params=payload.to_json()
        )
        if not response.content:
            return None
        return RemoteConfigurationManagementValidationResult(
            raw_element=response.json()
        )

    async def get(self, job_id: str) -> "RemoteConfigurationManagementJob":
        """Gets the specified remote configuration management job

        :param job_id: The ID of the required job
        :return: The specified job
        """
        response = (
            await self.__http_client.make_request(f"{self.ENDPOINT}/{job_id}")
        ).json()
        return RemoteConfigurationManagementJob(raw_element=response)


class EntityType(Enum):
    ACTIVE_GATE = "ACTIVE_GATE"
    ONE_AGENT = "ONE_AGENT"


class AttributeType(Enum):
    GROUP = "group"
    HOST_GROUP = "hostGroup"
    HOST_PROPERTY = "hostProperty"
    HOST_TAG = "hostTag"
    NETWORK_ZONE = "networkZone"


class OperationType(Enum):
    CLEAR = "clear"
    SET = "set"


class RemoteConfigurationManagementOperation(DynatraceObject):
    """Definition of a single remote configuration management operation"""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.attribute: AttributeType = AttributeType(raw_element["attribute"])
        self.operation: OperationType = OperationType(raw_element["operation"])
        self.value: str | None = raw_element.get("value")

    def to_json(self) -> dict[str, Any]:
        return {
            "attribute": self.attribute.value,
            "operation": self.operation.value,
            "value": self.value,
        }

    @staticmethod
    def build(
        attribute: AttributeType, operation: OperationType, value: str | None = None
    ) -> "RemoteConfigurationManagementOperation":
        return RemoteConfigurationManagementOperation(
            raw_element={
                "attribute": attribute.value,
                "operation": operation.value,
                "value": value,
            }
        )


class RemoteConfigurationManagementOperationActiveGateRequest:
    """Remote configuration management operation creation request"""

    def __init__(
        self,
        entities: list[str],
        operations: list[RemoteConfigurationManagementOperation],
    ):
        self.entities = entities
        self.operations = operations

    def to_json(self) -> dict[str, Any]:
        return {
            "entities": self.entities,
            "operations": [op.to_json() for op in self.operations],
        }


class RemoteConfigurationManagementOperationOneAgentRequest:
    """Remote configuration management operation creation request"""

    def __init__(
        self,
        entities: list[str],
        operations: list[RemoteConfigurationManagementOperation],
    ):
        self.entities = entities
        self.operations = operations

    def to_json(self) -> dict[str, Any]:
        return {
            "entities": self.entities,
            "operations": [op.to_json() for op in self.operations],
        }


class RemoteConfigurationManagementJob(DynatraceObject):
    """Remote configuration management job"""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.id: str = raw_element["id"]
        self.entity_type: EntityType = EntityType(raw_element["entityType"])
        self.start_time: str = raw_element["startTime"]
        self.end_time: str | None = raw_element.get("endTime")
        self.timeout_time: str | None = raw_element.get("timeoutTime")
        self.total_entities_count: int = raw_element["totalEntitiesCount"]
        self.processed_entities_count: int = raw_element["processedEntitiesCount"]
        self.operations: list[RemoteConfigurationManagementOperation] = [
            RemoteConfigurationManagementOperation(raw_element=op)
            for op in raw_element.get("operations", [])
        ]


class RemoteConfigurationManagementJobSummary(DynatraceObject):
    """Remote configuration management job with basic data"""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.id: str = raw_element["id"]
        self.entity_type: EntityType = EntityType(raw_element["entityType"])
        self.start_time: str = raw_element["startTime"]
        self.end_time: str | None = raw_element.get("endTime")


class RemoteConfigurationManagementJobPreview(DynatraceObject):
    """A preview of remote configuration management job"""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.attribute: AttributeType = AttributeType(raw_element["attribute"])
        self.operation: OperationType = OperationType(raw_element["operation"])
        self.value: str | None = raw_element.get("value")
        self.already_configured_entities_count: int = raw_element[
            "alreadyConfiguredEntitiesCount"
        ]
        self.target_entities_count: int = raw_element["targetEntitiesCount"]


class RemoteConfigurationManagementValidationResult(DynatraceObject):
    """The result of remote configuration management validation"""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.invalid_entities: list[
            RemoteConfigurationManagementEntityValidationError
        ] = [
            RemoteConfigurationManagementEntityValidationError(raw_element=error)
            for error in raw_element.get("invalidEntities", [])
        ]
        self.invalid_operations: list[
            RemoteConfigurationManagementOperationValidationError
        ] = [
            RemoteConfigurationManagementOperationValidationError(raw_element=error)
            for error in raw_element.get("invalidOperations", [])
        ]


class RemoteConfigurationManagementEntityValidationError(DynatraceObject):
    """Entity validation error for remote configuration management"""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.entity: str = raw_element["entity"]
        self.reasons: list[str] = raw_element.get("reasons", [])


class RemoteConfigurationManagementOperationValidationError(DynatraceObject):
    """Validation error of remote configuration management operation definition"""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.attribute: AttributeType | None = (
            AttributeType(raw_element["attribute"])
            if "attribute" in raw_element
            else None
        )
        self.operation: OperationType | None = (
            OperationType(raw_element["operation"])
            if "operation" in raw_element
            else None
        )
        self.value: str | None = raw_element.get("value")
        self.reason: str = raw_element["reason"]
