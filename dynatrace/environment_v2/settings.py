from __future__ import annotations

from datetime import datetime
from typing import Any

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList
from dynatrace.utils import (
    raw_optional_bool,
    raw_optional_datetime,
    raw_optional_object,
    raw_optional_str,
    raw_required_bool,
)


class SettingService:
    OBJECTS_ENDPOINT = "/api/v2/settings/objects"
    SCHEMAS_ENDPOINT = "/api/v2/settings/schemas"
    EFFECTIVE_VALUES_ENDPOINT = "/api/v2/settings/effectiveValues"

    def __init__(self, http_client: HttpClient):
        self.__http_client = http_client

    async def list_schemas(
        self, fields: str | None = None
    ) -> PaginatedList[SchemaStub]:
        """Lists all settings schemas available in your environment"""

        return await PaginatedList(
            SchemaStub,
            self.__http_client,
            target_url=self.SCHEMAS_ENDPOINT,
            list_item="items",
            target_params={"fields": fields},
        ).initialize()

    async def list_objects(
        self,
        schema_id: str | None = None,
        scope: str | None = None,
        external_ids: str | None = None,
        fields: str | None = None,
        filter: str | None = None,
        sort: str | None = None,
        page_size: str | None = None,
        admin_access: bool | None = None,
    ) -> PaginatedList[SettingsObject]:
        """Lists settings

        :return: a list of settings with details
        """
        params = {
            "schemaIds": schema_id,
            "scopes": scope,
            "fields": fields,
            "externalIds": external_ids,
            "filter": filter,
            "sort": sort,
            "pageSize": page_size,
            "adminAccess": admin_access,
        }
        return await PaginatedList(
            SettingsObject,
            self.__http_client,
            target_url=self.OBJECTS_ENDPOINT,
            list_item="items",
            target_params=params,
        ).initialize()

    async def list_effective_values(
        self,
        scope: str,
        schema_ids: str | None = None,
        fields: str | None = None,
        page_size: int | None = None,
        admin_access: bool | None = None,
    ) -> PaginatedList[EffectiveSettingsValue]:
        """Lists effective settings values for selected schemas at a selected scope"""

        params = {
            "schemaIds": schema_ids,
            "scope": scope,
            "fields": fields,
            "pageSize": page_size,
            "adminAccess": admin_access,
        }
        return await PaginatedList(
            EffectiveSettingsValue,
            self.__http_client,
            target_url=self.EFFECTIVE_VALUES_ENDPOINT,
            list_item="items",
            target_params=params,
        ).initialize()

    async def create_object(
        self,
        validate_only: bool | None = False,
        body: list[SettingsObjectCreate] | SettingsObjectCreate | None = None,
        admin_access: bool | None = None,
    ):
        """
        Creates a new settings object or validates the provided settigns object

        :param validate_only: If true, the request runs only validation of the submitted settings objects, without saving them
        :param body: The JSON body of the request. Contains the settings objects
        """
        query_params = {"validateOnly": validate_only, "adminAccess": admin_access}

        if isinstance(body, SettingsObjectCreate):
            body = [body]

        request_body = [] if body is None else [o.json() for o in body]

        response = (
            await self.__http_client.make_request(
                self.OBJECTS_ENDPOINT,
                params=request_body,
                method="POST",
                query_params=query_params,
            )
        ).json()
        return response

    async def get_object(self, object_id: str, admin_access: bool | None = None):
        """Gets parameters of specified settings object

        :param object_id: the ID of the object
        :return: a Settings object
        """
        query_params = {"adminAccess": admin_access}
        response = (
            await self.__http_client.make_request(
                f"{self.OBJECTS_ENDPOINT}/{object_id}", query_params=query_params
            )
        ).json()
        return SettingsObject(raw_element=response)

    async def update_object(
        self,
        object_id: str,
        body: SettingsObjectUpdate | None = None,
        validate_only: bool | None = None,
        admin_access: bool | None = None,
    ):
        """Updates an existing settings object

        :param object_id: the ID of the object
        :param value: the JSON body of the request. Contains updated parameters of the settings object.
        """
        query_params = {"validateOnly": validate_only, "adminAccess": admin_access}
        params = body.json() if body else None
        return await self.__http_client.make_request(
            f"{self.OBJECTS_ENDPOINT}/{object_id}",
            params=params,
            method="PUT",
            query_params=query_params,
        )

    async def delete_object(
        self,
        object_id: str,
        update_token: str | None = None,
        admin_access: bool | None = None,
    ):
        """Deletes the specified object

        :param object_id: the ID of the object
        :param update_token: The update token of the object. You can use it to detect simultaneous modifications by different users
        :return: HTTP response
        """
        query_params = {"updateToken": update_token, "adminAccess": admin_access}
        return await self.__http_client.make_request(
            f"{self.OBJECTS_ENDPOINT}/{object_id}",
            method="DELETE",
            query_params=query_params,
        )


class ModificationInfo(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.deleteable: bool = raw_required_bool(raw_element, "deletable")
        self.first: bool | None = raw_optional_bool(raw_element, "first")
        self.modifiable: bool = raw_required_bool(raw_element, "modifiable")
        self.modifiable_paths: list[str] = raw_element.get("modifiablePaths", [])
        self.movable: bool = raw_required_bool(raw_element, "movable")
        self.non_modifiable_paths: list[str] = raw_element.get("nonModifiablePaths", [])


class SettingsObject(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.object_id: str | None = raw_optional_str(raw_element, "objectId")
        self.value: dict[str, Any] | None = raw_element.get("value")
        self.author: str | None = raw_optional_str(raw_element, "author")
        self.created: datetime | None = raw_optional_datetime(raw_element, "created")
        self.created_by: str | None = raw_optional_str(raw_element, "createdBy")
        self.external_id: str | None = raw_optional_str(raw_element, "externalId")
        self.modification_info: ModificationInfo | None = raw_optional_object(
            raw_element,
            "modificationInfo",
            lambda value: ModificationInfo(self._http_client, self._headers, value),
        )
        self.modified: datetime | None = raw_optional_datetime(raw_element, "modified")
        self.modified_by: str | None = raw_optional_str(raw_element, "modifiedBy")
        self.schema_id: str | None = raw_optional_str(raw_element, "schemaId")
        self.schema_version: str | None = raw_optional_str(raw_element, "schemaVersion")
        self.scope: str | None = raw_optional_str(raw_element, "scope")
        self.search_summary: str | None = raw_optional_str(raw_element, "searchSummary")
        self.summary: str | None = raw_optional_str(raw_element, "summary")
        self.update_token: str | None = raw_optional_str(raw_element, "updateToken")


class SettingsObjectCreate:
    def __init__(
        self,
        schema_id: str,
        value: dict,
        scope: str,
        external_id: str | None = None,
        insert_after: str | None = None,
        object_id: str | None = None,
        schema_version: str | None = None,
    ):
        self.schema_id = schema_id
        self.value = value
        self.scope = scope
        self.external_id = external_id
        self.insert_after = insert_after
        self.object_id = object_id
        self.schema_version = schema_version

    def json(self) -> dict:
        body: dict[str, Any] = {
            "schemaId": self.schema_id,
            "value": self.value,
            "scope": self.scope,
        }
        if self.external_id:
            body["externalId"] = self.external_id
        if self.insert_after:
            body["insertAfter"] = self.insert_after
        if self.object_id:
            body["objectId"] = self.object_id
        if self.schema_version:
            body["schemaVersion"] = self.schema_version
        return body


class SettingsObjectUpdate:
    def __init__(
        self,
        value: dict,
        insert_after: str | None = None,
        insert_before: str | None = None,
        schema_version: str | None = None,
        update_token: str | None = None,
    ):
        self.value = value
        self.insert_after = insert_after
        self.insert_before = insert_before
        self.schema_version = schema_version
        self.update_token = update_token

    def json(self) -> dict:
        body: dict[str, Any] = {"value": self.value}
        if self.insert_after:
            body["insertAfter"] = self.insert_after
        if self.insert_before:
            body["insertBefore"] = self.insert_before
        if self.schema_version:
            body["schemaVersion"] = self.schema_version
        if self.update_token:
            body["updateToken"] = self.update_token
        return body


class SchemaStub(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.display_name = raw_element["displayName"]
        self.latest_schema_version = raw_element["latestSchemaVersion"]
        self.schema_id = raw_element["schemaId"]


class EffectiveSettingsValue(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.author: str | None = raw_element.get("author")
        self.created: datetime | None = raw_optional_datetime(raw_element, "created")
        self.created_by: str | None = raw_element.get("createdBy")
        self.external_id: str | None = raw_element.get("externalId")
        self.modified: datetime | None = raw_optional_datetime(raw_element, "modified")
        self.modified_by: str | None = raw_element.get("modifiedBy")
        self.origin: str | None = raw_element.get("origin")
        self.schema_id: str | None = raw_element.get("schemaId")
        self.schema_version: str | None = raw_element.get("schemaVersion")
        self.search_summary: str | None = raw_element.get("searchSummary")
        self.summary: str | None = raw_element.get("summary")
        self.value: Any | None = raw_element.get("value")
