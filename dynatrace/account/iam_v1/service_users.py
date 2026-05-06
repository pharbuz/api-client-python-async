"""Account service users management API wrappers."""

from typing import Any

from httpx import Response

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient


class AccountServiceUsersService:
    """
    /iam/v1 Service users management API

    - POST /iam/v1/accounts/{accountUuid}/service-users
    - GET /iam/v1/accounts/{accountUuid}/service-users
    - GET /iam/v1/accounts/{accountUuid}/service-users/{userUuid}
    - PUT /iam/v1/accounts/{accountUuid}/service-users/{userUuid}
    - DELETE /iam/v1/accounts/{accountUuid}/service-users/{userUuid}
    """

    def __init__(self, http_client: HttpClient) -> None:
        self.__http_client = http_client

    async def create(
        self,
        account_uuid: str,
        name: str,
        description: str | None = None,
    ) -> "ServiceUser":
        """Create a new service user in an account."""
        body = {"name": name}
        if description:
            body["description"] = description
        resp = (
            await self.__http_client.make_request(
                f"/iam/v1/accounts/{account_uuid}/service-users",
                method="POST",
                json=body,
            )
        ).json()
        return ServiceUser(raw_element=resp)

    async def list(
        self,
        account_uuid: str,
        page: int | None = None,
        page_size: int | None = None,
        page_key: str | None = None,
    ) -> "ServiceUsersPage":
        """List all service users assigned to account."""
        params = {}
        if page is not None:
            params["page"] = page
        if page_size is not None:
            params["page-size"] = page_size
        if page_key is not None:
            params["page-key"] = page_key

        resp = (
            await self.__http_client.make_request(
                f"/iam/v1/accounts/{account_uuid}/service-users",
                params=params,
            )
        ).json()
        return ServiceUsersPage(raw_element=resp)

    async def get(self, account_uuid: str, user_uuid: str) -> "ServiceUser":
        """Get service user by uuid."""
        resp = (
            await self.__http_client.make_request(
                f"/iam/v1/accounts/{account_uuid}/service-users/{user_uuid}"
            )
        ).json()
        return ServiceUser(raw_element=resp)

    async def update(
        self,
        account_uuid: str,
        user_uuid: str,
        name: str | None = None,
        description: str | None = None,
    ) -> Response:
        """Update name and description of service user in an account."""
        body = {}
        if name is not None:
            body["name"] = name
        if description is not None:
            body["description"] = description
        return await self.__http_client.make_request(
            f"/iam/v1/accounts/{account_uuid}/service-users/{user_uuid}",
            method="PUT",
            json=body,
        )

    async def delete(self, account_uuid: str, user_uuid: str) -> Response:
        """Delete a service user from an account."""
        return await self.__http_client.make_request(
            f"/iam/v1/accounts/{account_uuid}/service-users/{user_uuid}",
            method="DELETE",
        )


# Response models
class ServiceUser(DynatraceObject):
    """Service user object."""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.user_uuid: str | None = raw_element.get("userUuid")
        self.name: str | None = raw_element.get("name")
        self.description: str | None = raw_element.get("description")
        self.created_at: str | None = raw_element.get("createdAt")
        self.created_by: str | None = raw_element.get("createdBy")
        self.updated_at: str | None = raw_element.get("updatedAt")
        self.updated_by: str | None = raw_element.get("updatedBy")
        self.group_uuids: list[str] = raw_element.get("groupUuids", [])


class ServiceUsersPage(DynatraceObject):
    """Page of service users."""

    def _create_from_raw_data(self, raw_element: dict[str, Any]):
        self.items: list[ServiceUser] = [
            ServiceUser(raw_element=e) for e in raw_element.get("items", [])
        ]
        self.next_page_key: str | None = raw_element.get("nextPageKey")
        self.page_size: int | None = raw_element.get("pageSize")
