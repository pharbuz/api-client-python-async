"""Account group management API wrappers."""

import builtins
from typing import Any, Union

from httpx import Response

from dynatrace.dynatrace_object import DynatraceObject
from dynatrace.http_client import HttpClient


class AccountGroupsService:
    """
    /iam/v1 Group management API

    - GET /iam/v1/accounts/{accountUuid}/groups
    - POST /iam/v1/accounts/{accountUuid}/groups
    - GET /iam/v1/accounts/{accountUuid}/groups/{groupUuid}/users
    - PUT /iam/v1/accounts/{accountUuid}/groups/{groupUuid}
    - DELETE /iam/v1/accounts/{accountUuid}/groups/{groupUuid}
    """

    def __init__(self, http_client: HttpClient) -> None:
        self.__http_client = http_client

    async def list(self, account_uuid: str) -> "GroupList":
        """List all user groups of an account."""
        resp = (
            await self.__http_client.make_request(
                f"/iam/v1/accounts/{account_uuid}/groups"
            )
        ).json()
        return GroupList(raw_element=resp)

    async def create(
        self, account_uuid: str, groups: builtins.list[dict[str, Any]]
    ) -> builtins.list["Group"]:
        """Create new user groups."""
        resp = (
            await self.__http_client.make_request(
                f"/iam/v1/accounts/{account_uuid}/groups",
                method="POST",
                json=groups,
            )
        ).json()
        return [Group(raw_element=e) for e in resp]

    async def get_members(self, account_uuid: str, group_uuid: str) -> "GroupMembers":
        """List all members of a group."""
        resp = (
            await self.__http_client.make_request(
                f"/iam/v1/accounts/{account_uuid}/groups/{group_uuid}/users"
            )
        ).json()
        return GroupMembers(raw_element=resp)

    async def update(
        self,
        account_uuid: str,
        group_uuid: str,
        group_config: Union["GroupUpdateRequest", dict[str, Any]],
    ) -> Response:
        """Edit a user group."""
        if isinstance(group_config, GroupUpdateRequest):
            body = group_config.to_json()
        else:
            body = group_config
        return await self.__http_client.make_request(
            f"/iam/v1/accounts/{account_uuid}/groups/{group_uuid}",
            method="PUT",
            json=body,
        )

    async def delete(self, account_uuid: str, group_uuid: str) -> Response:
        """Delete a user group."""
        return await self.__http_client.make_request(
            f"/iam/v1/accounts/{account_uuid}/groups/{group_uuid}",
            method="DELETE",
        )


# Response models
class Group(DynatraceObject):
    """Group object."""

    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.uuid: str | None = raw_element.get("uuid")
        self.name: str | None = raw_element.get("name")
        self.description: str | None = raw_element.get("description")
        self.federated_attribute_values: list[str] = raw_element.get(
            "federatedAttributeValues", []
        )
        self.owner: str | None = raw_element.get("owner")
        self.created_at: str | None = raw_element.get("createdAt")
        self.updated_at: str | None = raw_element.get("updatedAt")

    def to_json(self) -> dict[str, Any]:
        return {
            "uuid": self.uuid,
            "name": self.name,
            "description": self.description,
            "federatedAttributeValues": self.federated_attribute_values,
        }


class GroupList(DynatraceObject):
    """List of groups."""

    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.count: int | None = raw_element.get("count")
        self.items: list[Group] = [
            Group(raw_element=e) for e in raw_element.get("items", [])
        ]


class GroupUser(DynatraceObject):
    """User in a group."""

    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.uid: str | None = raw_element.get("uid")
        self.email: str | None = raw_element.get("email")
        self.name: str | None = raw_element.get("name")
        self.surname: str | None = raw_element.get("surname")
        self.user_status: str | None = raw_element.get("userStatus")
        self.emergency_contact: bool | None = raw_element.get("emergencyContact")


class GroupMembers(DynatraceObject):
    """Members of a group."""

    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.count: int | None = raw_element.get("count")
        self.items: list[GroupUser] = [
            GroupUser(raw_element=e) for e in raw_element.get("items", [])
        ]


class GroupUpdateRequest(DynatraceObject):
    """Request for updating a group."""

    def __init__(
        self,
        name: str,
        description: str | None = None,
        federated_attribute_values: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.name: str | None = name
        self.description: str | None = description
        self.federated_attribute_values: list[str] = federated_attribute_values or []

    def _create_from_raw_data(self, raw_element: dict[str, Any]) -> None:
        self.name = raw_element.get("name")
        self.description = raw_element.get("description")
        self.federated_attribute_values = raw_element.get(
            "federatedAttributeValues", []
        )

    def to_json(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "federatedAttributeValues": self.federated_attribute_values,
        }
