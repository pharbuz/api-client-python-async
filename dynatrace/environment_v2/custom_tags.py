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
from typing import Any

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList
from dynatrace.utils import timestamp_to_string


class CustomTagService:
    ENDPOINT = "/api/v2/tags"

    def __init__(self, http_client: HttpClient) -> None:
        self.__http_client = http_client

    async def list(
        self,
        entity_selector: str,
        time_from: datetime | str | None = None,
        time_to: datetime | str | None = None,
    ) -> PaginatedList["METag"]:
        """
        Returns a list of custom tags
        :param entity_selector: specifies entities where you want to read tags
        :param time_from: The start of the requested timeframe.
        :param time_to: The end of the requested timeframe.

        :return: A list of METag objects
        """
        params = {
            "entitySelector": entity_selector,
            "from": timestamp_to_string(time_from),
            "to": timestamp_to_string(time_to),
        }

        return await PaginatedList(
            METag,
            self.__http_client,
            target_url=self.ENDPOINT,
            target_params=params,
            list_item="tags",
        ).initialize()

    async def post(
        self,
        entity_selector: str,
        tags: builtins.list["AddEntityTags"],
        time_from: datetime | str | None = None,
        time_to: datetime | str | None = None,
    ) -> "AddedEntityTags":
        """
        Adds custom tags to the specified entities
        :param entity_selector: specifies entities where you want to read tags
        :param time_from: The start of the requested timeframe.
        :param time_to: The end of the requested timeframe.
        :param tags: list of Tag objects Tag = { key, value(optional)}

        :return: AddedEntityTags
        """
        query_params = {
            "entitySelector": entity_selector,
            "from": timestamp_to_string(time_from),
            "to": timestamp_to_string(time_to),
        }
        body = {
            "tags": [t.to_json() for t in tags],
        }
        response = (
            await self.__http_client.make_request(
                self.ENDPOINT, params=body, method="POST", query_params=query_params
            )
        ).json()
        return AddedEntityTags(raw_element=response)

    async def delete(
        self,
        key: str,
        entity_selector: str,
        value: str | None = None,
        delete_all_with_key: bool | None = None,
        time_from: datetime | str | None = None,
        time_to: datetime | str | None = None,
    ) -> "DeletedEntityTags":
        """
        Deletes the specified tag from the specified entities
        """
        params = {
            "key": key,
            "entitySelector": entity_selector,
            "deleteAllWithKey": delete_all_with_key,
            "value": value,
            "from": timestamp_to_string(time_from),
            "to": timestamp_to_string(time_to),
        }
        response = await self.__http_client.make_request(
            self.ENDPOINT, params=params, method="DELETE"
        )
        return DeletedEntityTags(raw_element=response.json())


class AddedEntityTags(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.matched_entities_count: int = raw_element.get("matchedEntitiesCount", 0)
        self.applied_tags: list[METag] = [
            METag(raw_element=tag) for tag in raw_element.get("appliedTags", [])
        ]


class DeletedEntityTags(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.matched_entities_count: int = raw_element.get("matchedEntitiesCount", 0)


class AddEntityTags:
    def __init__(self, key: str, value: str | None = None):
        self.key = key
        self.value = value

    def to_json(self) -> dict[str, str]:
        return {"key": self.key, "value": self.value}


class METag(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.context: TagContext = TagContext(raw_element["context"])
        self.key: str = raw_element["key"]
        self.value: str | None = raw_element.get("value")
        self.string_representation: str | None = raw_element.get("stringRepresentation")

    def to_json(self) -> dict[str, Any]:
        return {"context": str(self.context), "key": self.key, "value": self.value}


class TagContext(Enum):
    AWS = "AWS"
    AWS_GENERIC = "AWS_GENERIC"
    AZURE = "AZURE"
    CLOUD_FOUNDRY = "CLOUD_FOUNDRY"
    CONTEXTLESS = "CONTEXTLESS"
    ENVIRONMENT = "ENVIRONMENT"
    GOOGLE_CLOUD = "GOOGLE_CLOUD"
    KUBERNETES = "KUBERNETES"
    GOOGLE_COMPUTE_ENGINE = "GOOGLE_COMPUTE_ENGINE"

    def __str__(self) -> str:
        return self.value
