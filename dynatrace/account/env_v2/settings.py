"""Account settings API wrappers."""

from datetime import datetime
from typing import Any

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.environment_v2.settings import SettingService as DtSettingsService
from dynatrace.environment_v2.settings import SettingsObject
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList
from dynatrace.utils import int64_to_datetime


class SettingService(DtSettingsService):
    EFFECTIVE_VALUES_ENDPOINT = "/api/v2/settings/effectiveValues"

    def __init__(self, http_client: HttpClient):
        super().__init__(http_client=http_client)
        self.__http_client = http_client

    # Account-level settings listing endpoints.
    async def list_objects(
        self,
        schema_id: str | None = None,
        scope: str | None = None,
        external_ids: str | None = None,
        fields: str | None = None,
        filter: str | None = None,
        sort: str | None = None,
        page_size: int | None = None,
        admin_access: bool | None = None,
    ) -> PaginatedList[SettingsObject]:
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
    ) -> PaginatedList["EffectiveSettingsValue"]:
        """Lists effective settings values for selected schemas at a selected scope."""

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


# Response models.
class EffectiveSettingsValue(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.author: str | None = raw_element.get("author")
        self.created: datetime | None = (
            int64_to_datetime(int(raw_element.get("created")))
            if raw_element.get("created")
            else None
        )
        self.created_by: str | None = raw_element.get("createdBy")
        self.external_id: str | None = raw_element.get("externalId")
        self.modified: datetime | None = (
            int64_to_datetime(int(raw_element.get("modified")))
            if raw_element.get("modified")
            else None
        )
        self.modified_by: str | None = raw_element.get("modifiedBy")
        self.origin: str | None = raw_element.get("origin")
        self.schema_id: str | None = raw_element.get("schemaId")
        self.schema_version: str | None = raw_element.get("schemaVersion")
        self.search_summary: str | None = raw_element.get("searchSummary")
        self.summary: str | None = raw_element.get("summary")
        self.value: Any | None = raw_element.get("value")
