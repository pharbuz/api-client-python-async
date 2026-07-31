"""Account settings API wrappers."""

from typing import Any

from httpx import Response

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.environment_v2.settings import EffectiveSettingsValue, SettingsObject
from dynatrace.environment_v2.settings import SettingService as DtSettingsService
from dynatrace.http_client import HttpClient
from dynatrace.pagination import PaginatedList


class SettingService(DtSettingsService):
    EFFECTIVE_VALUES_ENDPOINT = "/api/v2/settings/effectiveValues"

    def __init__(self, http_client: HttpClient):
        super().__init__(http_client=http_client)
        self.__http_client = http_client

    async def list_costcenters(
        self,
        account_uuid: str,
        page: int | None = None,
        page_size: int | None = None,
    ) -> "FieldValuesPage":
        """Lists all possible values for the costcenter field."""
        return await self._list_field_values(
            account_uuid, "costcenters", page, page_size
        )

    async def add_costcenters(
        self,
        account_uuid: str,
        values: list[str] | list["FieldValue"] | "FieldValuesRequest" | dict[str, Any],
    ) -> Response:
        """Adds the provided values to the costcenter field."""
        return await self._write_field_values(
            account_uuid, "costcenters", values, method="POST"
        )

    async def replace_costcenters(
        self,
        account_uuid: str,
        values: list[str] | list["FieldValue"] | "FieldValuesRequest" | dict[str, Any],
    ) -> Response:
        """Replaces the current values of the costcenter field."""
        return await self._write_field_values(
            account_uuid, "costcenters", values, method="PUT"
        )

    async def delete_costcenter(self, account_uuid: str, key: str) -> Response:
        """Deletes a value by key on the costcenter field."""
        return await self.__http_client.make_request(
            f"/v1/accounts/{account_uuid}/settings/costcenters/{key}",
            method="DELETE",
        )

    async def list_products(
        self,
        account_uuid: str,
        page: int | None = None,
        page_size: int | None = None,
    ) -> "FieldValuesPage":
        """Lists all possible values for the product field."""
        return await self._list_field_values(account_uuid, "products", page, page_size)

    async def add_products(
        self,
        account_uuid: str,
        values: list[str] | list["FieldValue"] | "FieldValuesRequest" | dict[str, Any],
    ) -> Response:
        """Adds the provided values to the product field."""
        return await self._write_field_values(
            account_uuid, "products", values, method="POST"
        )

    async def replace_products(
        self,
        account_uuid: str,
        values: list[str] | list["FieldValue"] | "FieldValuesRequest" | dict[str, Any],
    ) -> Response:
        """Replaces the current values of the product field."""
        return await self._write_field_values(
            account_uuid, "products", values, method="PUT"
        )

    async def delete_product(self, account_uuid: str, key: str) -> Response:
        """Deletes a value by key on the product field."""
        return await self.__http_client.make_request(
            f"/v1/accounts/{account_uuid}/settings/products/{key}",
            method="DELETE",
        )

    # Account-level settings listing endpoints.
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

    async def _list_field_values(
        self,
        account_uuid: str,
        field: str,
        page: int | None,
        page_size: int | None,
    ) -> "FieldValuesPage":
        params = {
            "page": page,
            "page-size": page_size,
        }
        resp = (
            await self.__http_client.make_request(
                f"/v1/accounts/{account_uuid}/settings/{field}",
                params=params,
            )
        ).json()
        return FieldValuesPage(raw_element=resp)

    async def _write_field_values(
        self,
        account_uuid: str,
        field: str,
        values: list[str] | list["FieldValue"] | "FieldValuesRequest" | dict[str, Any],
        method: str,
    ) -> Response:
        return await self.__http_client.make_request(
            f"/v1/accounts/{account_uuid}/settings/{field}",
            method=method,
            json=self._field_values_body(values),
        )

    @staticmethod
    def _field_values_body(
        values: list[str] | list["FieldValue"] | "FieldValuesRequest" | dict[str, Any],
    ) -> dict[str, Any]:
        if isinstance(values, FieldValuesRequest):
            return values.to_json()
        if isinstance(values, dict):
            return values
        return {
            "values": [
                value.to_json() if isinstance(value, FieldValue) else {"key": value}
                for value in values
            ]
        }


# Response models.
class FieldValue(DynatraceObject):
    def __init__(self, key: str | None = None, **kwargs: Any) -> None:
        self.key: str | None = None
        super().__init__(**kwargs)
        if key is not None:
            self.key = key

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.key = raw_element.get("key")

    def to_json(self) -> dict[str, Any]:
        return {"key": self.key}


class FieldValuesRequest(DynatraceObject):
    def __init__(
        self,
        values: list[str] | list[FieldValue] | None = None,
        **kwargs: Any,
    ) -> None:
        self.values: list[FieldValue] = []
        super().__init__(**kwargs)
        if values is not None:
            self.values = [
                value if isinstance(value, FieldValue) else FieldValue(key=value)
                for value in values
            ]

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.values = [
            FieldValue(raw_element=value) for value in raw_element.get("values", [])
        ]

    def to_json(self) -> dict[str, Any]:
        return {"values": [value.to_json() for value in self.values]}


class FieldValuesPage(DynatraceObject):
    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.records: list[FieldValue] = [
            FieldValue(raw_element=record) for record in raw_element.get("records", [])
        ]
        self.has_next_page: bool | None = raw_element.get("hasNextPage")
